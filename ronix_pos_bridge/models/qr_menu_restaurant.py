from odoo import fields, models


class QrMenuRestaurant(models.Model):
    _inherit = 'qr.menu.restaurant'

    pos_config_id = fields.Many2one(
        'pos.config',
        string='Linked POS Config',
        ondelete='set null',
        index=True,
    )
