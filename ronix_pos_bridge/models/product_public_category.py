from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    pos_category_id = fields.Many2one(
        'pos.category',
        string='Linked POS Category',
        ondelete='set null',
        index=True,
    )
