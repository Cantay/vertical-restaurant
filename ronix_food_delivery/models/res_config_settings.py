from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    food_demo_data_loaded = fields.Boolean(
        string='Demo Data Loaded',
        config_parameter='ronix_food_delivery.demo_data_loaded',
    )

    def action_load_demo_data(self):
        self.env['food.demo.data.loader'].load_demo_data()
        self.env['ir.config_parameter'].sudo().set_param(
            'ronix_food_delivery.demo_data_loaded', 'True'
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Demo Data',
                'message': 'Demo veriler başarıyla yüklendi.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_unload_demo_data(self):
        self.env['food.demo.data.loader'].unload_demo_data()
        self.env['ir.config_parameter'].sudo().set_param(
            'ronix_food_delivery.demo_data_loaded', ''
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Demo Data',
                'message': 'Demo veriler başarıyla kaldırıldı.',
                'type': 'success',
                'sticky': False,
            },
        }
