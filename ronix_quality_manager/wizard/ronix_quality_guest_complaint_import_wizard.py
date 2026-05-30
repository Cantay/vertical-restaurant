from odoo import fields, models
from odoo.exceptions import ValidationError


class RonixQualityGuestComplaintImportWizard(models.TransientModel):
    _name = 'ronix.quality.guest.complaint.import.wizard'
    _description = 'Ronix Quality Guest Complaint Import Wizard'

    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'ronix_quality_guest_complaint_import_attachment_rel',
        'wizard_id',
        'attachment_id',
        string='Excel Dosyalari',
    )
    result_message = fields.Html(string='Import Sonucu', readonly=True, sanitize=False)

    def action_import_files(self):
        self.ensure_one()
        if not self.attachment_ids:
            raise ValidationError('En az bir Excel dosyasi yuklemelisiniz.')
        result = self.env['ronix.quality.guest.complaint.report'].import_from_xlsx_attachments(
            self.attachment_ids,
            location_id=self.location_id.id,
        )
        lines = ['<div><strong>Toplam eklenen satir:</strong> %s</div>' % result['total_imported']]
        for item in result['results']:
            lines.append(
                '<div><strong>%s</strong>: %s</div>' % (item['filename'], item['message'])
            )
        self.result_message = ''.join(lines)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Misafir Sikayet Excel Import',
            'res_model': 'ronix.quality.guest.complaint.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
