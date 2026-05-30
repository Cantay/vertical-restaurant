# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FoodDeliveryAddress(models.Model):
    _name = 'food.delivery.address'
    _description = 'Food Delivery Address'

    name = fields.Char(string='Address Title', required=True, help="e.g. Home, Work, Gym")
    address_details = fields.Char(string='Address Details', required=True)
    city = fields.Char(string='City')
    district = fields.Char(string='District')
    address_directions = fields.Char(string='Address Directions')
    lat = fields.Float(string='Latitude', digits=(12, 6))
    lng = fields.Float(string='Longitude', digits=(12, 6))
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', required=True)
    is_default = fields.Boolean(string='Is Default', default=False)

    @api.model
    def create(self, vals):
        if vals.get('is_default'):
            self.search([('partner_id', '=', vals.get('partner_id')), ('is_default', '=', True)]).write({'is_default': False})
        return super(FoodDeliveryAddress, self).create(vals)

    def write(self, vals):
        if vals.get('is_default'):
            self.search([('partner_id', '=', self.partner_id.id), ('is_default', '=', True)]).write({'is_default': False})
        return super(FoodDeliveryAddress, self).write(vals)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    food_address_ids = fields.One2many('food.delivery.address', 'partner_id', string='Food Delivery Addresses')
    current_food_address_id = fields.Many2one('food.delivery.address', string='Current Food Delivery Address', 
                                             domain="[('partner_id', '=', id)]")
