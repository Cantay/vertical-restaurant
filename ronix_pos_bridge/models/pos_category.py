from odoo import fields, models


class PosCategory(models.Model):
    _inherit = 'pos.category'

    public_category_id = fields.Many2one(
        'product.public.category',
        string='Linked Public Category',
        ondelete='set null',
        index=True,
    )
