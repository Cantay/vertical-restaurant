from odoo import fields, models


class FoodRestaurant(models.Model):
    _inherit = 'food.restaurant'

    pos_config_id = fields.Many2one(
        'pos.config',
        string='Linked POS Config',
        ondelete='set null',
        index=True,
    )

    def action_sync_to_pos(self):
        """Food Delivery -> POS: push food products into POS.
        If no POS config linked, show selection wizard or create one."""
        self.ensure_one()

        if not self.pos_config_id:
            # Try to find an unlinked POS config
            existing_configs = self.env['pos.config'].search([
                ('food_restaurant_id', '=', False),
            ])
            if existing_configs:
                # Show selection dialog
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'POS Yapılandırması Seç',
                    'res_model': 'pos.config',
                    'view_mode': 'list,form',
                    'target': 'new',
                    'domain': [('food_restaurant_id', '=', False)],
                    'context': {
                        'food_restaurant_link_id': self.id,
                        'create': False,
                    },
                }
            else:
                # Create a new POS config and link
                pos_config = self.env['pos.config'].create({
                    'name': self.name,
                    'food_restaurant_id': self.id,
                })
                self.pos_config_id = pos_config.id

        # Now sync
        pos_config = self.pos_config_id
        pos_config.food_restaurant_id = self.id
        pos_config.action_sync_from_food_delivery()
