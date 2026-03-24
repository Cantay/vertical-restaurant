from odoo import fields, models


class FoodRestaurant(models.Model):
    _inherit = 'food.restaurant'

    qr_menu_restaurant_id = fields.Many2one(
        'qr.menu.restaurant',
        string='Linked QR Menu Restaurant',
        ondelete='set null',
    )

    def action_sync_to_qr_menu(self):
        self.ensure_one()
        QrRest = self.env['qr.menu.restaurant']

        if self.qr_menu_restaurant_id:
            qr_rest = self.qr_menu_restaurant_id
        else:
            # Check if a qr.menu.restaurant already links back
            qr_rest = QrRest.search([('food_restaurant_id', '=', self.id)], limit=1)
            if not qr_rest:
                qr_rest = QrRest.create({
                    'name': self.name,
                    'food_restaurant_id': self.id,
                })
            self.qr_menu_restaurant_id = qr_rest.id

        # Ensure reverse link
        if not qr_rest.food_restaurant_id or qr_rest.food_restaurant_id.id != self.id:
            qr_rest.food_restaurant_id = self.id

        # Perform the sync
        qr_rest._sync_from_food_restaurant(self)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sync Tamamlandı',
                'message': f'"{self.name}" QR Menüye başarıyla senkronize edildi.',
                'type': 'success',
                'sticky': False,
            },
        }
