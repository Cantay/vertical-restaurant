from odoo import fields, models


class RestaurantTable(models.Model):
    _inherit = 'restaurant.table'

    qr_menu_table_id = fields.Many2one(
        'qr.menu.table',
        string='Linked QR Table',
        ondelete='set null',
        index=True,
    )
