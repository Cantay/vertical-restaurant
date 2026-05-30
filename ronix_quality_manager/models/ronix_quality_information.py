import os

from odoo import api, fields, models


class RonixQualityInformation(models.Model):
    _name = 'ronix.quality.information'
    _description = 'Ronix Quality Information'
    _order = 'publish_date desc, sequence asc, id desc'

    name = fields.Char(string='Baslik', required=True)
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one(
        'ronix.quality.information.category',
        string='Kategori',
        domain="[('active', '=', True)]",
    )
    publish_date = fields.Date(
        string='Yayin Tarihi',
        required=True,
        default=fields.Date.context_today,
    )
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    body = fields.Html(string='Icerik', sanitize=True, translate=True)
    attachment_ids = fields.One2many(
        'ronix.quality.information.attachment',
        'information_id',
        string='Ekler',
    )
    attachment_count = fields.Integer(compute='_compute_attachment_count')
    active = fields.Boolean(default=True)
    website_published = fields.Boolean(string='Web Sitesinde Goster', default=True)
    website_url = fields.Char(string='Web Sitesi URL', compute='_compute_website_url')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/bilgilendirmeler'

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }


class RonixQualityInformationCategory(models.Model):
    _name = 'ronix.quality.information.category'
    _description = 'Ronix Quality Information Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'sequence asc, name asc, id asc'

    name = fields.Char(string='Kategori Adi', required=True)
    sequence = fields.Integer(default=10)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    parent_id = fields.Many2one(
        'ronix.quality.information.category',
        string='Ust Kategori',
        index=True,
        ondelete='cascade',
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        'ronix.quality.information.category',
        'parent_id',
        string='Alt Kategoriler',
    )
    information_ids = fields.One2many(
        'ronix.quality.information',
        'category_id',
        string='Bilgilendirmeler',
    )
    active = fields.Boolean(default=True)


class RonixQualityInformationAttachment(models.Model):
    _name = 'ronix.quality.information.attachment'
    _description = 'Ronix Quality Information Attachment'
    _order = 'sequence asc, id asc'

    information_id = fields.Many2one(
        'ronix.quality.information',
        string='Bilgilendirme',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Etiket')
    datas = fields.Binary(string='Dosya', required=True, attachment=True)
    datas_fname = fields.Char(string='Dosya Adi')
    download_url = fields.Char(string='Indirme URL', compute='_compute_download_url')
    icon_class = fields.Char(string='Ikon Sinifi', compute='_compute_icon_class')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') and vals.get('datas_fname'):
                vals['name'] = vals['datas_fname']
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if vals.get('datas_fname') and not vals.get('name'):
            vals['name'] = vals['datas_fname']
        return super().write(vals)

    def _compute_download_url(self):
        for record in self:
            record.download_url = '/ronix-quality/information/attachment/%s' % record.id if record.id else False

    @api.depends('datas_fname', 'name')
    def _compute_icon_class(self):
        icon_map = {
            '.pdf': 'fa-file-pdf-o',
            '.doc': 'fa-file-word-o',
            '.docx': 'fa-file-word-o',
            '.xls': 'fa-file-excel-o',
            '.xlsx': 'fa-file-excel-o',
            '.ppt': 'fa-file-powerpoint-o',
            '.pptx': 'fa-file-powerpoint-o',
            '.zip': 'fa-file-archive-o',
            '.rar': 'fa-file-archive-o',
            '.png': 'fa-file-image-o',
            '.jpg': 'fa-file-image-o',
            '.jpeg': 'fa-file-image-o',
            '.webp': 'fa-file-image-o',
            '.txt': 'fa-file-text-o',
        }
        for record in self:
            filename = record.datas_fname or record.name or ''
            extension = os.path.splitext(filename)[1].lower()
            record.icon_class = icon_map.get(extension, 'fa-file-o')
