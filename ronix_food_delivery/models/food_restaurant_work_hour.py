# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FoodRestaurantWorkHour(models.Model):
    _name = 'food.restaurant.work.hour'
    _description = 'Restaurant Working Hours'
    _order = 'day_of_week, start_time'

    restaurant_id = fields.Many2one('food.restaurant', string='Restaurant', required=True, ondelete='cascade')
    
    day_of_week = fields.Selection([
        ('0', 'Pazartesi'),
        ('1', 'Salı'),
        ('2', 'Çarşamba'),
        ('3', 'Perşembe'),
        ('4', 'Cuma'),
        ('5', 'Cumartesi'),
        ('6', 'Pazar')
    ], string='Day of Week', required=True)
    
    start_time = fields.Float(string='Start Time', required=True, default=9.0)
    end_time = fields.Float(string='End Time', required=True, default=22.0)

    @api.constrains('start_time', 'end_time')
    def _check_time_range(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("Bitiş saati, başlangıç saatinden büyük olmalıdır.")
            if record.start_time < 0 or record.start_time > 24 or record.end_time < 0 or record.end_time > 24:
                raise ValidationError("Saatler 0 ile 24 arasında olmalıdır.")
