import json

from odoo import api, fields, models


class RonixQualityButcheryTrackingForm(models.Model):
    _name = 'ronix.quality.butchery.tracking.form'
    _description = 'Ronix Quality Butchery Tracking Form'
    _order = 'tracking_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    tracking_date = fields.Date(string='Form Tarihi', required=True, default=fields.Date.context_today)
    operator_name = fields.Char(string='İşlemi Yapan Adı Soyadı')
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    line_ids = fields.One2many(
        'ronix.quality.butchery.tracking.form.line',
        'form_id',
        string='Ürünler',
    )
    line_count = fields.Integer(compute='_compute_line_count')
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    active = fields.Boolean(default=True)

    @api.depends('tracking_date')
    def _compute_name(self):
        for record in self:
            date_text = fields.Date.to_string(record.tracking_date) if record.tracking_date else 'Yeni'
            record.name = 'Kasaphane Ürün İzleme Formu - %s' % date_text

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/kasaphane-urun-izleme-formu'

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('ronix_quality_manager.action_report_butchery_tracking_form').report_action(self)


class RonixQualityButcheryTrackingFormLine(models.Model):
    _name = 'ronix.quality.butchery.tracking.form.line'
    _description = 'Ronix Quality Butchery Tracking Form Line'
    _order = 'sequence asc, id asc'

    form_id = fields.Many2one(
        'ronix.quality.butchery.tracking.form',
        string='Form',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    product_name = fields.Char(string='Ürünün Adı', required=True)
    brand_name = fields.Char(string='Marka')
    batch_no = fields.Char(string='Ürün Parti Numarası')
    expiry_date = fields.Date(string='Son Kullanma Tarihi')
    cold_room = fields.Boolean(string='Soğuk Oda')
    running_water = fields.Boolean(string='Akar Su')
    thaw_start_date = fields.Date(string='Çözdürme Başlangıç Tarihi')
    thaw_start_time = fields.Char(string='Çözdürme Başlangıç Saati')
    thaw_start_temperature = fields.Float(string='Çözdürme Ürün Başlangıç Sıcaklığı', digits=(16, 2))
    thaw_end_date = fields.Date(string='Çözdürme Bitiş Tarihi')
    thaw_end_time = fields.Char(string='Çözdürme Bitiş Saati')
    thaw_end_temperature = fields.Float(string='Çözdürme Ürün Bitiş Sıcaklığı', digits=(16, 2))
    delivered_section = fields.Many2many(
        'ronix.quality.butchery.section',
        'ronix_quality_butchery_tracking_line_section_rel',
        'line_id',
        'section_id',
        string='Verildiği Bölüm',
    )

    @api.model
    def parse_frontend_lines(self, payload):
        try:
            rows = json.loads(payload or '[]')
        except json.JSONDecodeError:
            rows = []
        commands = []
        for row in rows:
            if isinstance(row, dict):
                values = self._prepare_frontend_line_vals(row)
                if values:
                    commands.append(fields.Command.create(values))
        return commands

    @api.model
    def _prepare_frontend_line_vals(self, row):
        delivered_section_ids = self._to_int_list(row.get('delivered_section'))
        values = {
            'product_name': (row.get('product_name') or '').strip(),
            'brand_name': (row.get('brand_name') or '').strip(),
            'batch_no': (row.get('batch_no') or '').strip(),
            'expiry_date': row.get('expiry_date') or False,
            'cold_room': bool(row.get('cold_room')),
            'running_water': bool(row.get('running_water')),
            'thaw_start_date': row.get('thaw_start_date') or False,
            'thaw_start_time': (row.get('thaw_start_time') or '').strip(),
            'thaw_start_temperature': self._to_float(row.get('thaw_start_temperature')),
            'thaw_end_date': row.get('thaw_end_date') or False,
            'thaw_end_time': (row.get('thaw_end_time') or '').strip(),
            'thaw_end_temperature': self._to_float(row.get('thaw_end_temperature')),
        }
        if not any(values.values()) and not delivered_section_ids:
            return False
        values['delivered_section'] = [(6, 0, delivered_section_ids)]
        if not values['product_name']:
            values['product_name'] = 'Yeni Ürün'
        return values

    @api.model
    def _to_float(self, value):
        if value in (None, '', False):
            return False
        try:
            return float(str(value).replace(',', '.'))
        except (TypeError, ValueError):
            return False

    @api.model
    def _to_int(self, value):
        if value in (None, '', False):
            return False
        try:
            return int(value)
        except (TypeError, ValueError):
            return False

    @api.model
    def _to_int_list(self, value):
        if value in (None, '', False):
            return []
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value[:1] == '[':
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = [value]
        if not isinstance(value, list):
            value = [value]
        ids = []
        for item in value:
            if isinstance(item, (list, tuple)):
                ids.extend(self._to_int_list(item))
                continue
            item_id = self._to_int(item)
            if item_id:
                ids.append(item_id)
        return list(dict.fromkeys(ids))


class RonixQualityButcherySection(models.Model):
    _name = 'ronix.quality.butchery.section'
    _description = 'Ronix Quality Butchery Section'
    _order = 'sequence asc, name asc, id asc'

    name = fields.Char(string='Bölüm Adı', required=True)
    code = fields.Char(string='Kod')
    sequence = fields.Integer(default=10)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    active = fields.Boolean(default=True)
