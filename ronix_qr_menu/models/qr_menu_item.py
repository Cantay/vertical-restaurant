from odoo import models, fields, api


class QrMenuItem(models.Model):
    _name = 'qr.menu.item'
    _description = 'QR Menu Item'
    _order = 'sequence, name'

    # Basic
    restaurant_id = fields.Many2one('qr.menu.restaurant', string='Restaurant', required=True, ondelete='cascade')
    category_id = fields.Many2one('qr.menu.category', string='Category', required=True, ondelete='restrict',
                                  domain="[('restaurant_id', '=', restaurant_id)]")
    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)
    price = fields.Monetary(string='Price', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', related='restaurant_id.currency_id')

    # Content & Nutrition
    ingredients = fields.Html(string='Ingredients', translate=True, sanitize=True)
    allergen_ids = fields.Many2many('qr.menu.allergen', string='Allergens')
    calories = fields.Float(string='Calories (kcal)')
    protein = fields.Float(string='Protein (g)')
    carbs = fields.Float(string='Carbohydrates (g)')
    fat = fields.Float(string='Fat (g)')
    preparation_time = fields.Integer(string='Preparation Time (min)')

    # Diet Tags
    is_vegetarian = fields.Boolean(string='Vegetarian')
    is_vegan = fields.Boolean(string='Vegan')
    is_gluten_free = fields.Boolean(string='Gluten Free')
    is_spicy = fields.Boolean(string='Spicy')

    # AR
    ar_model_3d = fields.Binary(string='3D Model (GLB)', attachment=True)
    ar_model_filename = fields.Char(string='3D Model Filename')
    has_ar = fields.Boolean(string='Has AR', compute='_compute_has_ar', store=True)

    # Ordering
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_available = fields.Boolean(string='Available', default=True)

    @api.depends('ar_model_3d')
    def _compute_has_ar(self):
        for rec in self:
            rec.has_ar = bool(rec.ar_model_3d)
