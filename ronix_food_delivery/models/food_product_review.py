# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FoodProductReview(models.Model):
    _name = 'food.product.review'
    _description = 'Food Product Review'
    _order = 'create_date desc'

    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', string='Customer', store=True)
    order_id = fields.Many2one('sale.order', string='Order', ondelete='cascade')
    rating = fields.Integer(string='Rating', default=5, required=True, group_operator="avg")
    tag_ids = fields.Many2many('food.review.tag', string='Tags', domain=[('category', '=', 'product')])
    comment = fields.Text(string='Comment')
    
    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if record.rating < 1 or record.rating > 5:
                raise models.ValidationError("Rating must be between 1 and 5.")
