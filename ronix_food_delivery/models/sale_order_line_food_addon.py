# -*- coding: utf-8 -*-
from odoo import fields, models, api

class SaleOrderLineFoodAddon(models.Model):
    _name = 'sale.order.line.food.addon'
    _description = 'Food Addon Selection on Order Line'

    line_id = fields.Many2one('sale.order.line', string='Order Line', required=True, ondelete='cascade')
    addon_id = fields.Many2one('food.product.addon', string='Addon', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    currency_id = fields.Many2one('res.currency', related='line_id.currency_id', string='Currency', readonly=True)
    price_unit = fields.Monetary(related='addon_id.extra_price', string='Price Per Unit', currency_field='currency_id', readonly=True)
    price_total = fields.Monetary(compute='_compute_price_total', string='Total Price', currency_field='currency_id', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_total(self):
        for record in self:
            record.price_total = record.quantity * record.price_unit

    @api.depends('addon_id', 'quantity')
    def _compute_display_name(self):
        for record in self:
            if record.addon_id:
                record.display_name = f"{record.addon_id.name} x{record.quantity}"
            else:
                record.display_name = "Addon"
