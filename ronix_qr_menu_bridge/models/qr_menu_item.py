from odoo import fields, models


class QrMenuItem(models.Model):
    _inherit = 'qr.menu.item'

    food_product_id = fields.Many2one(
        'product.template',
        string='Linked Food Product',
        ondelete='set null',
        index=True,
    )
    food_item_rating = fields.Float(
        string='Food Rating',
        digits=(2, 1),
        readonly=True,
    )
    food_item_review_count = fields.Integer(
        string='Food Review Count',
        readonly=True,
    )
