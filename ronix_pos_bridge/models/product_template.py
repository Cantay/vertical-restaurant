from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_enable_in_pos(self):
        """Quick action to enable this product in POS."""
        self.write({'available_in_pos': True, 'sale_ok': True})

    def action_enable_as_food(self):
        """Quick action to flag this product as a food delivery item."""
        self.write({'is_food': True})
