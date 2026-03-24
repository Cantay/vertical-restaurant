# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FoodRestaurantReview(models.Model):
    _name = 'food.restaurant.review'
    _description = 'Food Restaurant Review'
    _order = 'create_date desc'

    restaurant_id = fields.Many2one('food.restaurant', string='Restaurant', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', string='Customer', store=True)
    order_id = fields.Many2one('sale.order', string='Order', ondelete='cascade')
    rating = fields.Integer(string='Rating', default=5, required=True, group_operator="avg")
    food_rating = fields.Integer(string='Food Rating', default=5, group_operator="avg")
    tag_ids = fields.Many2many('food.review.tag', string='Tags', domain=[('category', '=', 'restaurant')])
    comment = fields.Text(string='Comment')
    
    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if record.rating < 1 or record.rating > 5:
                raise models.ValidationError("Rating must be between 1 and 5.")
