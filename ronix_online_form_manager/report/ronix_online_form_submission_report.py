from odoo import models


class ReportRonixOnlineFormSubmission(models.AbstractModel):
    _name = 'report.ronix_online_form_manager.rfm_pdf'
    _description = 'Ronix Cevrimici Form PDF Raporu'

    def _get_report_values(self, docids, data=None):
        docs = self.env['ronix.online.form.submission'].browse(docids).exists()
        return {
            'doc_ids': docs.ids,
            'doc_model': 'ronix.online.form.submission',
            'docs': docs,
            'report_groups': docs._get_report_groups(),
        }
