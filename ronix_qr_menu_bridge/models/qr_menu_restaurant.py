import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DAY_NAMES = {
    '0': 'Pazartesi', '1': 'Salı', '2': 'Çarşamba',
    '3': 'Perşembe', '4': 'Cuma', '5': 'Cumartesi', '6': 'Pazar',
}


class QrMenuRestaurant(models.Model):
    _inherit = 'qr.menu.restaurant'

    # --- Link field ---
    food_restaurant_id = fields.Many2one(
        'food.restaurant',
        string='Linked Food Restaurant',
        ondelete='set null',
        index=True,
    )

    # --- Synced rating fields ---
    food_rating = fields.Float(string='Rating', digits=(2, 1), readonly=True)
    food_rating_avg = fields.Float(string='Food Rating', digits=(2, 1), readonly=True)
    food_review_count = fields.Integer(string='Review Count', readonly=True)

    # --- Work hours ---
    work_hours_html = fields.Html(string='Work Hours', readonly=True, sanitize=False)
    always_open = fields.Boolean(string='Always Open (24/7)', readonly=True)

    # ==========================================
    # Button: Pull from Food Delivery
    # ==========================================
    def action_pull_from_food_delivery(self):
        self.ensure_one()
        if not self.food_restaurant_id:
            raise UserError("Bağlı bir Food Delivery restoranı yok. Önce bağlantıyı kurun.")
        self._sync_from_food_restaurant(self.food_restaurant_id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync Tamamlandı',
                'message': f'"{self.name}" QR Menü başarıyla güncellendi.',
                'type': 'success',
                'sticky': False,
            },
        }

    # ==========================================
    # Core Sync Logic
    # ==========================================
    def _sync_from_food_restaurant(self, food_rest):
        self.ensure_one()

        # 1) Restaurant-level fields
        vals = {
            'name': food_rest.name,
            'description': food_rest.description,
            'image_1920': food_rest.image_1920,
            'phone': food_rest.phone,
            'address': food_rest.address,
            'is_open': food_rest.is_open,
            'food_rating': food_rest.rating,
            'food_rating_avg': food_rest.food_rating_avg,
            'food_review_count': food_rest.review_count,
            'always_open': food_rest.always_open,
            'work_hours_html': self._build_work_hours_html(food_rest),
        }
        self.write(vals)

        # 2) Sync categories
        self._sync_categories(food_rest)

        # 3) Sync products/items
        self._sync_items(food_rest)

    def _build_work_hours_html(self, food_rest):
        if food_rest.always_open:
            return '<p><strong>7/24 Açık</strong></p>'
        if not food_rest.work_hour_ids:
            return '<p class="text-muted">Çalışma saati belirtilmemiş.</p>'

        lines = []
        for wh in food_rest.work_hour_ids.sorted(key=lambda w: (w.day_of_week, w.start_time)):
            day_label = DAY_NAMES.get(wh.day_of_week, wh.day_of_week)
            start_h, start_m = divmod(int(wh.start_time * 60), 60)
            end_h, end_m = divmod(int(wh.end_time * 60), 60)
            lines.append(
                f'<tr><td class="pe-3 fw-bold">{day_label}</td>'
                f'<td>{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d}</td></tr>'
            )
        return f'<table class="table table-sm table-borderless mb-0">{"".join(lines)}</table>'

    def _sync_categories(self, food_rest):
        QrCategory = self.env['qr.menu.category']
        existing_map = {
            cat.food_category_id.id: cat
            for cat in self.category_ids
            if cat.food_category_id
        }

        for seq, food_cat in enumerate(food_rest.category_ids, start=1):
            if food_cat.id in existing_map:
                existing_map[food_cat.id].write({
                    'name': food_cat.name,
                    'image': food_cat.image_1920,
                    'sequence': seq * 10,
                })
            else:
                QrCategory.create({
                    'restaurant_id': self.id,
                    'food_category_id': food_cat.id,
                    'name': food_cat.name,
                    'image': food_cat.image_1920,
                    'sequence': seq * 10,
                })

    def _sync_items(self, food_rest):
        QrItem = self.env['qr.menu.item']
        food_products = self.env['product.template'].search([
            ('is_food', '=', True),
            ('food_restaurant_id', '=', food_rest.id),
        ])

        existing_map = {
            item.food_product_id.id: item
            for item in self.item_ids
            if item.food_product_id
        }

        # Map: food category id -> qr.menu.category id
        cat_map = {
            cat.food_category_id.id: cat.id
            for cat in self.category_ids
            if cat.food_category_id
        }

        for product in food_products:
            # Determine QR category
            qr_cat_id = False
            for pub_cat in product.public_categ_ids:
                if pub_cat.id in cat_map:
                    qr_cat_id = cat_map[pub_cat.id]
                    break
            if not qr_cat_id and self.category_ids:
                qr_cat_id = self.category_ids[0].id

            if not qr_cat_id:
                _logger.warning("Bridge sync: skipping product %s — no QR category.", product.name)
                continue

            ingredients_html = self._build_ingredients_html(product)

            item_vals = {
                'name': product.name,
                'description': product.description_sale or '',
                'image_1920': product.image_1920,
                'price': product.list_price,
                'restaurant_id': self.id,
                'category_id': qr_cat_id,
                'ingredients': ingredients_html,
                'is_available': True,
                'food_product_id': product.id,
                'food_item_rating': product.food_rating,
                'food_item_review_count': product.food_review_count,
            }

            if product.id in existing_map:
                existing_map[product.id].write(item_vals)
            else:
                QrItem.create(item_vals)

    def _build_ingredients_html(self, product):
        if not product.food_addon_ids:
            return ''

        groups = {}
        for addon in product.food_addon_ids.sorted(key=lambda a: (a.group_name, a.sequence)):
            groups.setdefault(addon.group_name, []).append(addon)

        html_parts = []
        for group_name, addons in groups.items():
            html_parts.append(f'<h6 class="fw-bold mt-2">{group_name}</h6><ul class="mb-1">')
            for addon in addons:
                price_str = ''
                if addon.extra_price:
                    price_str = f' <span class="text-muted">(+{addon.extra_price:.2f})</span>'
                html_parts.append(f'<li>{addon.name}{price_str}</li>')
            html_parts.append('</ul>')

        return ''.join(html_parts)
