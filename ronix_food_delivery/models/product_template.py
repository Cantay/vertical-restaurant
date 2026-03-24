# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_food = fields.Boolean(string='Is Food Item', default=False)
    food_restaurant_id = fields.Many2one('food.restaurant', string='Restaurant')
    
    # Reviews & Ratings
    food_review_ids = fields.One2many('food.product.review', 'product_id', string='Reviews')
    food_rating = fields.Float(string='Food Rating', compute='_compute_food_rating', store=True, digits=(2, 1))
    food_review_count = fields.Integer(string='Food Review Count', compute='_compute_food_rating', store=True)
    
    # Favorites
    food_favorite_user_ids = fields.Many2many('res.users', 'food_product_favorite_rel', 'product_id', 'user_id', string='Favorited By')
    is_food_favorite = fields.Boolean(string='Is Favorite Food', compute='_compute_is_food_favorite', search='_search_is_food_favorite')
    
    # Extras and Options
    food_addon_ids = fields.One2many('food.product.addon', 'product_id', string='Extra Options/Add-ons')

    @api.depends('food_review_ids.rating')
    def _compute_food_rating(self):
        for product in self:
            if product.food_review_ids:
                total_rating = sum(product.food_review_ids.mapped('rating'))
                count = len(product.food_review_ids)
                product.food_rating = total_rating / count
                product.food_review_count = count
            else:
                product.food_rating = 0.0
                product.food_review_count = 0

    @api.depends_context('uid')
    def _compute_is_food_favorite(self):
        for product in self:
            product.is_food_favorite = self.env.user in product.food_favorite_user_ids

    def _search_is_food_favorite(self, operator, value):
        if operator == '=' and value:
            return [('food_favorite_user_ids', 'in', self.env.uid)]
        elif operator == '=' and not value:
            return [('food_favorite_user_ids', 'not in', self.env.uid)]
        return []

    def action_toggle_food_favorite(self):
        self.ensure_one()
        if self.env.user in self.food_favorite_user_ids:
            self.food_favorite_user_ids = [(3, self.env.user.id)]
        else:
            self.food_favorite_user_ids = [(4, self.env.user.id)]
