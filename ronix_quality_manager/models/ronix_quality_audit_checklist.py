from odoo import api, fields, models


class RonixQualityAuditGroup(models.Model):
    _name = 'ronix.quality.audit.group'
    _description = 'Ronix Quality Audit Group'
    _order = 'sequence asc, id asc'

    department_name = fields.Char(string='Departman Adi', required=True)
    sequence = fields.Integer(default=10)
    note = fields.Text(string='Kisa Not')
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    item_ids = fields.One2many(
        'ronix.quality.audit.item',
        'group_id',
        string='Kontrol Listesi Maddeleri',
    )
    item_count = fields.Integer(compute='_compute_item_count')
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(string='Web Sitesinde Goster', default=True)
    website_url = fields.Char(string='Web Sitesi URL', compute='_compute_website_url')

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/denetime-hazir-miyim'

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }


class RonixQualityAuditItem(models.Model):
    _name = 'ronix.quality.audit.item'
    _description = 'Ronix Quality Audit Item'
    _order = 'sequence asc, id asc'

    group_id = fields.Many2one(
        'ronix.quality.audit.group',
        string='Departman',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Yapilacak', required=True)
    note = fields.Text(string='Ek Not')
    active = fields.Boolean(default=True)
