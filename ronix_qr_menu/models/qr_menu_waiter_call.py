from odoo import models, fields


class QrMenuWaiterCall(models.Model):
    _name = 'qr.menu.waiter.call'
    _description = 'Waiter Call'
    _order = 'create_date desc'

    restaurant_id = fields.Many2one('qr.menu.restaurant', string='Restaurant', required=True, ondelete='cascade')
    table_id = fields.Many2one('qr.menu.table', string='Table', required=True, ondelete='cascade')
    call_type = fields.Selection([
        ('waiter', 'Call Waiter'),
        ('bill', 'Request Bill'),
        ('water', 'Request Water'),
        ('custom', 'Custom Request'),
    ], string='Call Type', required=True, default='waiter')
    custom_message = fields.Text(string='Message')

    state = fields.Selection([
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', required=True)

    acknowledged_by = fields.Many2one('res.users', string='Acknowledged By')
    acknowledged_at = fields.Datetime(string='Acknowledged At')
    completed_at = fields.Datetime(string='Completed At')

    def action_acknowledge(self):
        self.write({
            'state': 'acknowledged',
            'acknowledged_by': self.env.uid,
            'acknowledged_at': fields.Datetime.now(),
        })

    def action_complete(self):
        self.write({
            'state': 'completed',
            'completed_at': fields.Datetime.now(),
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})
