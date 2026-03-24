from odoo import models, fields, api


class QrMenuCategory(models.Model):
    _name = 'qr.menu.category'
    _description = 'QR Menu Category'
    _order = 'sequence, name'

    restaurant_id = fields.Many2one('qr.menu.restaurant', string='Restaurant', required=True, ondelete='cascade')
    name = fields.Char(string='Category Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    image = fields.Image(string='Image', max_width=512, max_height=512)
    icon = fields.Char(string='Icon Class', help='Remix icon class, e.g. ri-restaurant-line')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    item_ids = fields.One2many('qr.menu.item', 'category_id', string='Items')
    item_count = fields.Integer(compute='_compute_item_count', string='Item Count')

    @api.depends('item_ids')
    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)
