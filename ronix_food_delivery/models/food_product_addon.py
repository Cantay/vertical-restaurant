# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FoodProductAddon(models.Model):
    _name = 'food.product.addon'
    _description = 'Food Product Extra Option/Add-on'
    _order = 'group_name, sequence, name'

    product_id = fields.Many2one('product.template', string='Food Item', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    
    group_name = fields.Char(string='Group Name', required=True, help='e.g. İçecek Seç (İsteğe bağlı)')
    name = fields.Char(string='Option Name', required=True, help='e.g. Kola')
    
    extra_price = fields.Monetary(string='Extra Price', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', related='product_id.currency_id', string='Currency')

    selection_type = fields.Selection([
        ('select', 'Selection (Tick/Checkbox)'),
        ('quantity', 'Quantity (Numeric)')
    ], string='Selection Type', default='select', required=True)

    is_required = fields.Boolean(string='Required', default=False, help='User must select this option group')
    max_selections = fields.Integer(string='Max Selections', default=1, help='How many options can be selected from this group (0 = unlimited)')
