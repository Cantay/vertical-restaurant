from odoo import api, fields, models


class RonixQualityAnnouncement(models.Model):
    _name = 'ronix.quality.announcement'
    _description = 'Ronix Quality Announcement'
    _order = 'sequence asc, id desc'

    name = fields.Char(string='Baslik', required=True)
    sequence = fields.Integer(default=10)
    announcement_date = fields.Char(string='Tarih / Program')
    subtitle = fields.Char(string='Alt Baslik')
    body = fields.Html(string='Detay Icerigi', sanitize=True, translate=True)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(string='Web Sitesinde Goster', default=True)
    button_label = fields.Char(string='Buton Yazisi', default='Detaylar')
    website_url = fields.Char(string='Web Sitesi URL', compute='_compute_website_url')

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/duyurular/%s' % record.id if record.id else False

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url or '/duyurular',
            'target': 'new',
        }
