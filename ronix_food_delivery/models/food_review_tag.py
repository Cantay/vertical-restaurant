# -*- coding: utf-8 -*-
from odoo import fields, models

class FoodReviewTag(models.Model):
    _name = 'food.review.tag'
    _description = 'Food Review Tag'
    _order = 'sequence, name'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    icon = fields.Char(string='Remixicon Class', default='ri-chat-1-line')
    category = fields.Selection([
        ('restaurant', 'Restaurant'),
        ('product', 'Food Item')
    ], string='Category', default='restaurant', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
