from odoo import fields, models


class QrMenuTable(models.Model):
    _inherit = 'qr.menu.table'

    pos_table_id = fields.Many2one(
        'restaurant.table',
        string='Linked POS Table',
        ondelete='set null',
        index=True,
    )
