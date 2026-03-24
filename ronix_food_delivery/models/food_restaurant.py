# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FoodRestaurant(models.Model):
    _name = 'food.restaurant'
    _description = 'Food Delivery Restaurant'
    _inherit = ['image.mixin']
    _order = 'is_popular desc, rating desc, name'

    name = fields.Char(string='Restaurant Name', required=True)
    description = fields.Text(string='Description')
    manager_ids = fields.Many2many('res.users', 'food_restaurant_manager_rel', 'restaurant_id', 'user_id', string='Shop Managers', help="Users who can manage this restaurant")
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)
    
    # Categories
    category_ids = fields.Many2many('product.public.category', string='Categories')
    
    # Reviews & Ratings
    review_ids = fields.One2many('food.restaurant.review', 'restaurant_id', string='Reviews')
    rating = fields.Float(string='Rating', compute='_compute_restaurant_rating', store=True, digits=(2, 1))
    review_count = fields.Integer(string='Review Count', compute='_compute_restaurant_rating', store=True)
    food_rating_avg = fields.Float(string='Food Rating Average', compute='_compute_restaurant_rating', store=True, digits=(2, 1))

    # Metrics and Settings
    delivery_time_min = fields.Integer(string='Min Delivery Time (mins)', default=20)
    delivery_time_max = fields.Integer(string='Max Delivery Time (mins)', default=30)
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    min_order_amount = fields.Monetary(string='Minimum Order Amount', currency_field='currency_id', default=40.0)
    platform_commission_rate = fields.Float(string='Platform Komisyon Oranı (%)', digits=(16, 2), default=0.0)
    
    # Operations
    always_open = fields.Boolean(string='Always Open (24/7)', default=True, help="If checked, the restaurant is always open. Otherwise, working hours apply.")
    timezone = fields.Selection('_get_timezone_selection', string='Timezone', default='Europe/Istanbul', required=True)
    is_grocery = fields.Boolean(string='Is Grocery Store?', default=False, help="If checked, this store will be listed in the Grocery section.")
    work_hour_ids = fields.One2many('food.restaurant.work.hour', 'restaurant_id', string='Working Hours')
    
    is_open = fields.Boolean(string='Is Open Now', compute='_compute_is_open', search='_search_is_open')
    delivery_fee = fields.Monetary(string='Delivery Fee (Fixed)', currency_field='currency_id', default=0.0)
    
    # Dynamic Delivery Fee Configuration
    delivery_base_price = fields.Monetary(string='Delivery Base Price', currency_field='currency_id', default=0.0)
    delivery_km_price = fields.Monetary(string='Delivery KM Price', currency_field='currency_id', default=0.0)
    
    # Favorites
    favorite_user_ids = fields.Many2many('res.users', string='Favorited By')
    is_favorite = fields.Boolean(string='Is Favorite', compute='_compute_is_favorite', search='_search_is_favorite')
    
    # Location and Address
    address = fields.Text(string='Full Address')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    phone = fields.Char(string='Phone Number')
    
    # Flags
    active = fields.Boolean(string='Active', default=True)
    is_fast_delivery = fields.Boolean(string='Fast Delivery', default=False)
    has_campaign = fields.Boolean(string='Has Campaign', default=False)
    is_popular = fields.Boolean(string='Popular Restaurant', default=False)

    @api.depends_context('uid')
    def _compute_is_favorite(self):
        for restaurant in self:
            restaurant.is_favorite = self.env.user in restaurant.favorite_user_ids

    def _search_is_favorite(self, operator, value):
        if operator == '=' and value:
            return [('favorite_user_ids', 'in', self.env.uid)]
        elif operator == '=' and not value:
            return [('favorite_user_ids', 'not in', self.env.uid)]
        return []

    def _get_timezone_selection(self):
        import pytz
        return [(tz, tz) for tz in pytz.all_timezones]

    def _compute_is_open(self):
        from datetime import datetime
        import pytz
        
        now_utc = datetime.now(pytz.utc)
        
        for restaurant in self:
            if restaurant.always_open:
                restaurant.is_open = True
                continue
                
            if not restaurant.work_hour_ids:
                restaurant.is_open = False
                continue
                
            # Use restaurant's timezone
            user_tz = pytz.timezone(restaurant.timezone or 'Europe/Istanbul')
            now_local = now_utc.astimezone(user_tz)
            current_day = str(now_local.weekday())
            current_hour_float = now_local.hour + (now_local.minute / 60.0)
                
            # Check if current time falls within any of the defined working hours for today
            is_open_now = False
            for wh in restaurant.work_hour_ids.filtered(lambda h: h.day_of_week == current_day):
                if wh.start_time <= current_hour_float <= wh.end_time:
                    is_open_now = True
                    break
            
            restaurant.is_open = is_open_now

    def _search_is_open(self, operator, value):
        # Searching is tricky with per-restaurant timezones.
        # For simplicity and correctness in search, we'll use a slightly broader approach
        # or filter after search if performance allows.
        # But for 'is_open' filter in Odoo views, we'll try to match the logic.
        
        # Note: Search results might be slightly off for restaurants in very different TZs
        # if we don't calculate everything in SQL. For now, we'll use a Python-based filter
        # by searching all then filtering, as the number of restaurants is usually small.
        # However, for Odoo domain, we must return a leaf.
        
        all_restaurants = self.search([('active', '=', True)])
        if operator == '=' and value:
            ids = all_restaurants.filtered(lambda r: r.is_open).ids
            return [('id', 'in', ids)]
        elif operator == '=' and not value:
            ids = all_restaurants.filtered(lambda r: not r.is_open).ids
            return [('id', 'in', ids)]
        return []

    @api.depends('review_ids.rating', 'review_ids.food_rating')
    def _compute_restaurant_rating(self):
        for restaurant in self:
            if restaurant.review_ids:
                total_rating = sum(restaurant.review_ids.mapped('rating'))
                total_food_rating = sum(restaurant.review_ids.mapped('food_rating'))
                count = len(restaurant.review_ids)
                restaurant.rating = total_rating / count
                restaurant.food_rating_avg = total_food_rating / count
                restaurant.review_count = count
            else:
                restaurant.rating = 0.0
                restaurant.food_rating_avg = 0.0
                restaurant.review_count = 0

    def action_toggle_favorite(self):
        self.ensure_one()
        if self.env.user in self.favorite_user_ids:
            self.favorite_user_ids = [(3, self.env.user.id)]
        else:
            self.favorite_user_ids = [(4, self.env.user.id)]
