# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    food_line_addon_ids = fields.One2many('sale.order.line.food.addon', 'line_id', string='Food Addons')
    food_notes = fields.Text(string='Notes')
    food_addons_summary = fields.Char(
        compute='_compute_food_addons_summary',
        string='Yemek Ekstraları',
        store=False,
    )

    @api.depends('food_line_addon_ids', 'food_line_addon_ids.addon_id', 'food_line_addon_ids.quantity')
    def _compute_food_addons_summary(self):
        for line in self:
            parts = []
            for addon in line.food_line_addon_ids:
                if addon.addon_id:
                    parts.append(f"{addon.addon_id.name} x{addon.quantity}")
            line.food_addons_summary = ', '.join(parts) if parts else ''

    @api.depends('product_id', 'product_uom_qty', 'food_line_addon_ids')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for line in self:
            if line.product_id.is_food:
                addon_price = sum(line.food_line_addon_ids.mapped('price_total'))
                line.price_unit = line.product_id.list_price + addon_price
