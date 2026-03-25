from odoo import models, fields, api


class QrMenuRestaurant(models.Model):
    _name = 'qr.menu.restaurant'
    _description = 'QR Menu Restaurant'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Restaurant Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', store=True)
    manager_ids = fields.Many2many('res.users', string='Managers')

    table_ids = fields.One2many('qr.menu.table', 'restaurant_id', string='Tables')
    category_ids = fields.One2many('qr.menu.category', 'restaurant_id', string='Categories')
    item_ids = fields.One2many('qr.menu.item', 'restaurant_id', string='Menu Items')

    active = fields.Boolean(default=True)
    is_open = fields.Boolean(string='Currently Open', default=True)
    debug_mode = fields.Boolean(string='Debug Mode', default=False,
                                help='Enable debug logging in the QR menu frontend (browser console).')

    table_count = fields.Integer(compute='_compute_table_count', string='Table Count')
    category_count = fields.Integer(compute='_compute_category_count', string='Category Count')
    item_count = fields.Integer(compute='_compute_item_count', string='Item Count')

    qr_url = fields.Char(string='Menu URL', compute='_compute_qr_url')

    def _compute_qr_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.qr_url = f'{base_url}/qr-menu/{rec.id}' if rec.id else ''

    @api.depends('table_ids')
    def _compute_table_count(self):
        for rec in self:
            rec.table_count = len(rec.table_ids)

    @api.depends('category_ids')
    def _compute_category_count(self):
        for rec in self:
            rec.category_count = len(rec.category_ids)

    @api.depends('item_ids')
    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)
