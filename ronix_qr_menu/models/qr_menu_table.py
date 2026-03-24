import base64
import io

from odoo import models, fields, api

try:
    import qrcode
except ImportError:
    qrcode = None


class QrMenuTable(models.Model):
    _name = 'qr.menu.table'
    _description = 'QR Menu Table'
    _order = 'name'

    restaurant_id = fields.Many2one('qr.menu.restaurant', string='Restaurant', required=True, ondelete='cascade')
    name = fields.Char(string='Table Name', required=True)
    capacity = fields.Integer(string='Capacity', default=4)
    active = fields.Boolean(default=True)

    qr_url = fields.Char(string='QR URL', compute='_compute_qr_url')
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', store=True)

    @api.depends('restaurant_id')
    def _compute_qr_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if rec.id and rec.restaurant_id:
                rec.qr_url = f'{base_url}/qr-menu/{rec.restaurant_id.id}/table/{rec.id}'
            else:
                rec.qr_url = ''

    @api.depends('qr_url')
    def _compute_qr_code(self):
        for rec in self:
            if rec.qr_url and qrcode:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(rec.qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False

    def action_download_qr(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/image/qr.menu.table/{self.id}/qr_code/{self.name}_qr.png',
            'target': 'new',
        }
