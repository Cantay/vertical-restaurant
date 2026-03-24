# -*- coding: utf-8 -*-
from odoo import fields, models

class PaymentToken(models.Model):
    _inherit = 'payment.token'

    default_card = fields.Boolean(string="Default Card")
