from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    parent_id = fields.Many2one(
        'qr.menu.category',
        string='Parent Category',
        ondelete='restrict',
        domain="[('restaurant_id', '=', restaurant_id), ('id', '!=', id)]",
    )
    child_ids = fields.One2many('qr.menu.category', 'parent_id', string='Sub Categories')

    item_ids = fields.One2many('qr.menu.item', 'category_id', string='Items')
    item_count = fields.Integer(compute='_compute_item_count', string='Item Count')

    @api.depends('item_ids', 'child_ids', 'child_ids.item_ids')
    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids) + sum(len(child.item_ids) for child in rec.child_ids)

    @api.constrains('parent_id', 'restaurant_id')
    def _check_parent_category(self):
        for rec in self:
            if not rec.parent_id:
                continue
            if rec.parent_id == rec:
                raise ValidationError('Bir kategori kendisinin ust kategorisi olamaz.')
            if rec.parent_id.restaurant_id != rec.restaurant_id:
                raise ValidationError('Ust kategori ayni restorana ait olmalidir.')

            parent = rec.parent_id
            while parent:
                if parent == rec:
                    raise ValidationError('Kategori hiyerarsisinde dongu olusamaz.')
                parent = parent.parent_id
