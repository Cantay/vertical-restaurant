import re

from odoo import fields, http
from odoo.http import content_disposition, request


class RonixQualityOperationalNonconformityController(http.Controller):

    def _parse_int(self, value):
        if not value:
            return False
        try:
            return int(value)
        except (TypeError, ValueError):
            return False

    def _parse_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except (TypeError, ValueError):
            return False

    def _prepare_filter_values(self):
        model = request.env['ronix.quality.operational.nonconformity'].sudo()
        date_from = (request.params.get('date_from') or '').strip()
        date_to = (request.params.get('date_to') or '').strip()
        department_id = self._parse_int((request.params.get('department_id') or '').strip())
        state = (request.params.get('state') or '').strip()
        state_selection = dict(model._fields['state'].selection)
        selected_department = (
            model.env['ronix.quality.inspection.department'].browse(department_id).exists()
            if department_id else False
        )

        date_from_value = self._parse_date(date_from)
        date_to_value = self._parse_date(date_to)
        if state not in state_selection:
            state = ''

        records = model._get_public_report_records(
            date_from=date_from_value,
            date_to=date_to_value,
            department_id=selected_department.id if selected_department else False,
            state=state or False,
        )
        dashboard_rows = []
        for department_name in model._get_public_report_departments():
            department_records = records.filtered(lambda rec, dept=department_name: rec.department_name == dept)
            if not department_records:
                continue
            dashboard_rows.append({
                'department_name': department_name,
                'total': len(department_records),
                'new_job': len(department_records.filtered(lambda rec: rec.state == 'new_job')),
                'ongoing': len(department_records.filtered(lambda rec: rec.state == 'ongoing')),
                'ordered': len(department_records.filtered(lambda rec: rec.state == 'ordered')),
                'done': len(department_records.filtered(lambda rec: rec.state == 'done')),
            })
        return {
            'date_from': date_from,
            'date_to': date_to,
            'department_id': selected_department.id if selected_department else False,
            'department_name': selected_department.name if selected_department else '',
            'state': state,
            'state_selection': state_selection,
            'departments': model._get_filter_departments(),
            'records': records,
            'dashboard_rows': dashboard_rows,
            'summary_total': len(records),
            'summary_new_job': len(records.filtered(lambda rec: rec.state == 'new_job')),
            'summary_ongoing': len(records.filtered(lambda rec: rec.state == 'ongoing')),
            'summary_ordered': len(records.filtered(lambda rec: rec.state == 'ordered')),
            'summary_done': len(records.filtered(lambda rec: rec.state == 'done')),
        }

    @http.route(
        '/operasyonel-uygunsuzluk-raporu',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def operational_nonconformity_report_page(self, **_kwargs):
        values = self._prepare_filter_values()
        return request.render('ronix_quality_manager.operational_nonconformity_public_page', values)

    @http.route(
        '/operasyonel-uygunsuzluk-raporu/download',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
    )
    def download_operational_nonconformity_report(self, **_kwargs):
        values = self._prepare_filter_values()
        records = values['records']
        if not records:
            return request.redirect('/operasyonel-uygunsuzluk-raporu')

        pdf_content = request.env['ir.actions.report'].sudo().with_context(
            public_report_filters={
                'date_from': values['date_from'],
                'date_to': values['date_to'],
                'department_name': values['department_name'],
                'department_id': values['department_id'],
                'state': values['state'],
                'state_label': values['state_selection'].get(values['state'], ''),
            }
        )._render_qweb_pdf(
            'ronix_quality_manager.action_report_operational_nonconformity',
            res_ids=records.ids,
        )[0]

        filename_bits = ['operasyonel_uygunsuzluk_raporu']
        if values['department_name']:
            filename_bits.append(re.sub(r'[^a-zA-Z0-9_-]+', '_', values['department_name']).strip('_').lower())
        filename = '_'.join(bit for bit in filename_bits if bit) + '.pdf'
        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', str(len(pdf_content))),
                ('Content-Disposition', content_disposition(filename)),
                ('Cache-Control', 'private, max-age=0, no-store'),
            ],
        )
