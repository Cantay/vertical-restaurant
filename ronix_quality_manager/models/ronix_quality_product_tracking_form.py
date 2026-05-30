import json

from odoo import api, fields, models


class RonixQualityProductTrackingForm(models.Model):
    _name = 'ronix.quality.product.tracking.form'
    _description = 'Ronix Quality Product Tracking Form'
    _order = 'tracking_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    tracking_date = fields.Date(string='Form Tarihi', required=True, default=fields.Date.context_today)

    morning_buffet_time = fields.Char(string='Bufe Sunumu Sabah Saat')
    morning_hot_service_control_1 = fields.Float(string='Sabah Sicak Sunum 1. Kontrol', digits=(16, 2))
    morning_hot_service_control_2 = fields.Float(string='Sabah Sicak Sunum 2. Kontrol', digits=(16, 2))
    morning_cold_service_control_1 = fields.Float(string='Sabah Soguk Sunum 1. Kontrol', digits=(16, 2))
    morning_cold_service_control_2 = fields.Float(string='Sabah Soguk Sunum 2. Kontrol', digits=(16, 2))

    morning_cold_storage_time = fields.Char(string='Soguk Dolap Sabah Saat')
    morning_cold_storage_temp = fields.Float(string='Sabah Soguk Dolap (+4 C)', digits=(16, 2))
    morning_shock_storage_temp = fields.Float(string='Sabah Sok Dolap (-18 C)', digits=(16, 2))

    morning_environment_time = fields.Char(string='Ortam Sicakligi Sabah Saat')
    morning_environment_temperature = fields.Float(string='Sabah Ortam Sicakligi', digits=(16, 2))
    morning_environment_humidity = fields.Float(string='Sabah Nem', digits=(16, 2))

    evening_buffet_time = fields.Char(string='Bufe Sunumu Aksam Saat')
    evening_hot_service_control_1 = fields.Float(string='Aksam Sicak Sunum 1. Kontrol', digits=(16, 2))
    evening_hot_service_control_2 = fields.Float(string='Aksam Sicak Sunum 2. Kontrol', digits=(16, 2))
    evening_cold_service_control_1 = fields.Float(string='Aksam Soguk Sunum 1. Kontrol', digits=(16, 2))
    evening_cold_service_control_2 = fields.Float(string='Aksam Soguk Sunum 2. Kontrol', digits=(16, 2))

    evening_cold_storage_time = fields.Char(string='Soguk Dolap Aksam Saat')
    evening_cold_storage_temp = fields.Float(string='Aksam Soguk Dolap (+4 C)', digits=(16, 2))
    evening_shock_storage_temp = fields.Float(string='Aksam Sok Dolap (-18 C)', digits=(16, 2))

    evening_environment_time = fields.Char(string='Ortam Sicakligi Aksam Saat')
    evening_environment_temperature = fields.Float(string='Aksam Ortam Sicakligi', digits=(16, 2))
    evening_environment_humidity = fields.Float(string='Aksam Nem', digits=(16, 2))
    operator_name = fields.Char(string='Islemi Yapan Adi Soyadi')
    section_name = fields.Char(string='Bolum')
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )

    line_ids = fields.One2many(
        'ronix.quality.product.tracking.form.line',
        'form_id',
        string='Urunler',
    )
    line_count = fields.Integer(compute='_compute_line_count')
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    active = fields.Boolean(default=True)

    @api.depends('tracking_date')
    def _compute_name(self):
        for record in self:
            date_text = fields.Date.to_string(record.tracking_date) if record.tracking_date else 'Yeni'
            record.name = 'Urun Izleme Formu - %s' % date_text

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/urun-izleme-formu'

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }


class RonixQualityProductTrackingFormLine(models.Model):
    _name = 'ronix.quality.product.tracking.form.line'
    _description = 'Ronix Quality Product Tracking Form Line'
    _order = 'line_date asc, id asc'

    SAMPLE_PERIOD_SELECTION = [
        ('morning', 'Sabah Numune Alimi'),
        ('noon', 'Ogle Numune Alimi'),
        ('evening', 'Aksam Numune Alimi'),
    ]

    form_id = fields.Many2one(
        'ronix.quality.product.tracking.form',
        string='Form',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    sample_period = fields.Selection(
        SAMPLE_PERIOD_SELECTION,
        string='Numune Alim Donemi',
        required=True,
        default='morning',
    )
    line_date = fields.Date(string='Tarih', required=True, default=fields.Date.context_today)
    product_name = fields.Char(string='Urunun Adi', required=True)
    preparation_duration = fields.Integer(string='Hazirlik Suresi (dk)')

    cooking_duration = fields.Integer(string='Pisirme Suresi (dk)')
    cooking_end_temperature = fields.Float(string='Bitis Urun Merkez Sicakligi', digits=(16, 2))

    cooling_start_time = fields.Char(string='Sogutma Baslangic Saati')
    cooling_start_temperature = fields.Float(string='Sogutma Baslangic Sicakligi', digits=(16, 2))
    cooling_end_time = fields.Char(string='Sogutma Bitis Saati')
    cooling_end_temperature = fields.Float(string='Sogutma Bitis Sicakligi', digits=(16, 2))

    buffet_name = fields.Char(string='Bufe Ismi')
    banquet_cart_temperature = fields.Float(string='Banket Arabasinda Muhafaza Sicakligi', digits=(16, 2))

    witness_sample_taken = fields.Boolean(string='Sahit Numune Alindi Mi?')
    witness_product_temperature = fields.Float(string='Sahit Numune Urun Sicakligi', digits=(16, 2))

    returned_quantity = fields.Float(string='Geri Donen Miktar (Kuvet)', digits=(16, 2))
    destroyed_quantity = fields.Float(string='Imha Edilen Miktar (Kuvet)', digits=(16, 2))
    reheated_product_temperature = fields.Float(string='Tekrar Isitilan Urunun Ic Sicakligi', digits=(16, 2))
    @api.model
    def parse_frontend_lines(self, payload):
        try:
            rows = json.loads(payload or '[]')
        except json.JSONDecodeError:
            rows = []

        commands = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            values = self._prepare_frontend_line_vals(row)
            if not values:
                continue
            commands.append(fields.Command.create(values))
        return commands

    @api.model
    def _prepare_frontend_line_vals(self, row):
        values = {
            'sample_period': row.get('sample_period') or 'morning',
            'line_date': row.get('line_date') or False,
            'product_name': (row.get('product_name') or '').strip(),
            'preparation_duration': self._to_int(row.get('preparation_duration')),
            'cooking_duration': self._to_int(row.get('cooking_duration')),
            'cooking_end_temperature': self._to_float(row.get('cooking_end_temperature')),
            'cooling_start_time': (row.get('cooling_start_time') or '').strip(),
            'cooling_start_temperature': self._to_float(row.get('cooling_start_temperature')),
            'cooling_end_time': (row.get('cooling_end_time') or '').strip(),
            'cooling_end_temperature': self._to_float(row.get('cooling_end_temperature')),
            'buffet_name': (row.get('buffet_name') or '').strip(),
            'banquet_cart_temperature': self._to_float(row.get('banquet_cart_temperature')),
            'witness_sample_taken': bool(row.get('witness_sample_taken')),
            'witness_product_temperature': self._to_float(row.get('witness_product_temperature')),
            'returned_quantity': self._to_float(row.get('returned_quantity')),
            'destroyed_quantity': self._to_float(row.get('destroyed_quantity')),
            'reheated_product_temperature': self._to_float(row.get('reheated_product_temperature')),
        }
        if not any(values.get(key) for key in values if key != 'line_date'):
            return False
        if not values['line_date']:
            values['line_date'] = fields.Date.context_today(self)
        if not values['product_name']:
            values['product_name'] = 'Yeni Urun'
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
            return int(float(str(value).replace(',', '.')))
        except (TypeError, ValueError):
            return False
