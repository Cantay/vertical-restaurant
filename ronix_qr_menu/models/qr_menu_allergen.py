from odoo import models, fields


class QrMenuAllergen(models.Model):
    _name = 'qr.menu.allergen'
    _description = 'QR Menu Allergen'
    _order = 'sequence, name'

    name = fields.Char(string='Allergen Name', required=True, translate=True)
    icon = fields.Char(string='Icon Class', help='Remix icon class or emoji')
    sequence = fields.Integer(default=10)
