import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    food_restaurant_id = fields.Many2one(
        'food.restaurant',
        string='Linked Food Restaurant',
        ondelete='set null',
        index=True,
    )
    qr_menu_restaurant_id = fields.Many2one(
        'qr.menu.restaurant',
        string='Linked QR Menu Restaurant',
        ondelete='set null',
        index=True,
    )

    # -------------------------------------------------------------------------
    # Public Actions (called from UI buttons)
    # -------------------------------------------------------------------------

    def action_sync_to_food_delivery(self):
        """POS -> Food Delivery: push POS products as food items, map categories."""
        self.ensure_one()
        food_rest = self._ensure_food_restaurant_link()
        self._sync_categories_pos_to_food(food_rest)
        self._sync_products_pos_to_food(food_rest)
        return self._notify_success("POS -> Food Delivery sync tamamlandı.")

    def action_sync_from_food_delivery(self):
        """Food Delivery -> POS: pull food products into POS, map categories."""
        self.ensure_one()
        if not self.food_restaurant_id:
            raise UserError("Bağlı bir Food Delivery restoranı yok.")
        food_rest = self.food_restaurant_id
        self._sync_categories_food_to_pos(food_rest)
        self._sync_products_food_to_pos(food_rest)
        return self._notify_success("Food Delivery -> POS sync tamamlandı.")

    def action_sync_tables_to_qr_menu(self):
        """POS -> QR Menu: sync restaurant.table to qr.menu.table."""
        self.ensure_one()
        qr_rest = self._ensure_qr_restaurant_link()
        self._sync_tables_pos_to_qr(qr_rest)
        return self._notify_success("Masalar -> QR Menu sync tamamlandı.")

    def action_sync_all(self):
        """Full cascade sync: POS -> Food -> QR + tables."""
        self.ensure_one()
        food_rest = self._ensure_food_restaurant_link()
        self._sync_categories_pos_to_food(food_rest)
        self._sync_products_pos_to_food(food_rest)

        # Trigger existing bridge food->qr sync
        if hasattr(food_rest, 'action_sync_to_qr_menu'):
            food_rest.action_sync_to_qr_menu()

        # Sync tables
        qr_rest = self._ensure_qr_restaurant_link()
        self._sync_tables_pos_to_qr(qr_rest)
        return self._notify_success("Tam sync tamamlandı (POS -> Food -> QR).")

    # -------------------------------------------------------------------------
    # Link Helpers
    # -------------------------------------------------------------------------

    def _ensure_food_restaurant_link(self):
        """Find or create linked food.restaurant, set bidirectional link."""
        self.ensure_one()
        if self.food_restaurant_id:
            food_rest = self.food_restaurant_id
        else:
            food_rest = self.env['food.restaurant'].search(
                [('pos_config_id', '=', self.id)], limit=1
            )
            if not food_rest:
                food_rest = self.env['food.restaurant'].create({
                    'name': self.name,
                    'pos_config_id': self.id,
                    'always_open': True,
                })
            self.food_restaurant_id = food_rest.id
        if food_rest.pos_config_id != self:
            food_rest.pos_config_id = self.id
        return food_rest

    def _ensure_qr_restaurant_link(self):
        """Find or create linked qr.menu.restaurant, set bidirectional link."""
        self.ensure_one()
        if self.qr_menu_restaurant_id:
            qr_rest = self.qr_menu_restaurant_id
        else:
            qr_rest = self.env['qr.menu.restaurant'].search(
                [('pos_config_id', '=', self.id)], limit=1
            )
            if not qr_rest:
                qr_rest = self.env['qr.menu.restaurant'].create({
                    'name': self.name,
                    'pos_config_id': self.id,
                })
            self.qr_menu_restaurant_id = qr_rest.id
        if qr_rest.pos_config_id != self:
            qr_rest.pos_config_id = self.id
        # Cross-link with food.restaurant if both exist
        if self.food_restaurant_id:
            if not qr_rest.food_restaurant_id:
                qr_rest.food_restaurant_id = self.food_restaurant_id.id
            if not self.food_restaurant_id.qr_menu_restaurant_id:
                self.food_restaurant_id.qr_menu_restaurant_id = qr_rest.id
        return qr_rest

    # -------------------------------------------------------------------------
    # Category Sync
    # -------------------------------------------------------------------------

    def _sync_categories_pos_to_food(self, food_rest):
        """Map pos.category -> product.public.category, link to food.restaurant."""
        PubCat = self.env['product.public.category']
        pos_cats = self._get_pos_categories()

        for pos_cat in pos_cats:
            pub_cat = self._find_or_create_public_category(pos_cat)
            # Link to food restaurant's categories
            if pub_cat not in food_rest.category_ids:
                food_rest.write({'category_ids': [(4, pub_cat.id)]})

    def _sync_categories_food_to_pos(self, food_rest):
        """Map product.public.category -> pos.category for food restaurant."""
        for pub_cat in food_rest.category_ids:
            self._find_or_create_pos_category(pub_cat)

    def _get_pos_categories(self):
        """Get POS categories relevant to this config."""
        if self.limit_categories and self.iface_available_categ_ids:
            return self.iface_available_categ_ids
        # Get categories from products available in this POS
        products = self.env['product.product'].search([
            ('available_in_pos', '=', True),
        ])
        return products.mapped('pos_categ_ids')

    def _find_or_create_public_category(self, pos_cat):
        """Find or create a product.public.category linked to a pos.category."""
        PubCat = self.env['product.public.category']

        # First try by existing link
        if pos_cat.public_category_id:
            return pos_cat.public_category_id

        # Try by name match
        pub_cat = PubCat.search([('name', '=', pos_cat.name)], limit=1)
        if pub_cat:
            pub_cat.pos_category_id = pos_cat.id
            pos_cat.public_category_id = pub_cat.id
            return pub_cat

        # Create new
        pub_cat = PubCat.create({
            'name': pos_cat.name,
            'pos_category_id': pos_cat.id,
        })
        pos_cat.public_category_id = pub_cat.id
        return pub_cat

    def _find_or_create_pos_category(self, pub_cat):
        """Find or create a pos.category linked to a product.public.category."""
        PosCat = self.env['pos.category']

        # First try by existing link
        if pub_cat.pos_category_id:
            return pub_cat.pos_category_id

        # Try by name match
        pos_cat = PosCat.search([('name', '=', pub_cat.name)], limit=1)
        if pos_cat:
            pos_cat.public_category_id = pub_cat.id
            pub_cat.pos_category_id = pos_cat.id
            return pos_cat

        # Create new
        pos_cat = PosCat.create({
            'name': pub_cat.name,
            'public_category_id': pub_cat.id,
        })
        pub_cat.pos_category_id = pos_cat.id
        return pos_cat

    # -------------------------------------------------------------------------
    # Product Sync
    # -------------------------------------------------------------------------

    def _sync_products_pos_to_food(self, food_rest):
        """Set is_food=True and food_restaurant_id for POS products, map categories."""
        products = self.env['product.product'].search([
            ('available_in_pos', '=', True),
        ])
        for product in products:
            tmpl = product.product_tmpl_id
            vals = {}
            if not tmpl.is_food:
                vals['is_food'] = True
            if not tmpl.food_restaurant_id:
                vals['food_restaurant_id'] = food_rest.id

            # Map pos categories to public categories
            pub_cat_ids = []
            for pos_cat in tmpl.pos_categ_ids:
                if pos_cat.public_category_id and pos_cat.public_category_id not in tmpl.public_categ_ids:
                    pub_cat_ids.append((4, pos_cat.public_category_id.id))

            if vals:
                tmpl.write(vals)
            if pub_cat_ids:
                tmpl.write({'public_categ_ids': pub_cat_ids})

    def _sync_products_food_to_pos(self, food_rest):
        """Set available_in_pos=True for food products, map public cats to pos cats."""
        food_products = self.env['product.template'].search([
            ('is_food', '=', True),
            ('food_restaurant_id', '=', food_rest.id),
        ])
        for tmpl in food_products:
            vals = {}
            if not tmpl.available_in_pos:
                vals['available_in_pos'] = True
                vals['sale_ok'] = True

            # Map public categories to pos categories
            pos_cat_ids = []
            for pub_cat in tmpl.public_categ_ids:
                if pub_cat.pos_category_id and pub_cat.pos_category_id not in tmpl.pos_categ_ids:
                    pos_cat_ids.append((4, pub_cat.pos_category_id.id))

            if vals:
                tmpl.write(vals)
            if pos_cat_ids:
                tmpl.write({'pos_categ_ids': pos_cat_ids})

    # -------------------------------------------------------------------------
    # Table / Floor Sync
    # -------------------------------------------------------------------------

    def _sync_tables_pos_to_qr(self, qr_rest):
        """Sync restaurant.table -> qr.menu.table with floor name prefix."""
        QrTable = self.env['qr.menu.table']

        for floor in self.floor_ids:
            for table in floor.table_ids.filtered('active'):
                table_name = f"{floor.name} - Masa {table.table_number}"

                # Find existing linked QR table
                qr_table = QrTable.search([('pos_table_id', '=', table.id)], limit=1)
                table_vals = {
                    'name': table_name,
                    'capacity': table.seats,
                    'restaurant_id': qr_rest.id,
                    'pos_table_id': table.id,
                    'active': table.active,
                }

                if qr_table:
                    qr_table.write(table_vals)
                else:
                    qr_table = QrTable.create(table_vals)

                # Set reverse link
                if table.qr_menu_table_id != qr_table:
                    table.qr_menu_table_id = qr_table.id

    # -------------------------------------------------------------------------
    # Notification Helper
    # -------------------------------------------------------------------------

    def _notify_success(self, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync Tamamlandı',
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
