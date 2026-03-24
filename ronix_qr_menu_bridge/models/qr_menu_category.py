from odoo import fields, models


class QrMenuCategory(models.Model):
    _inherit = 'qr.menu.category'

    food_category_id = fields.Many2one(
        'product.public.category',
        string='Linked Food Category',
        ondelete='set null',
        index=True,
    )
