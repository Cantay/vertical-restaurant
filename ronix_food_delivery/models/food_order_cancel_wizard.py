# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class FoodOrderCancelWizard(models.TransientModel):
    _name = 'food.order.cancel.wizard'
    _description = 'Food Order Cancel Wizard'

    order_id = fields.Many2one('sale.order', string='Siparis', required=True, readonly=True)
    cancel_reason = fields.Text(string='Iptal Sebebi', required=True)

    def action_confirm_cancel(self):
        self.ensure_one()
        if not self.cancel_reason or not self.cancel_reason.strip():
            raise UserError('Iptal sebebi yazmadan devam edemezsiniz.')
        self.order_id.action_process_food_cancel(self.cancel_reason.strip())
        return {'type': 'ir.actions.act_window_close'}
