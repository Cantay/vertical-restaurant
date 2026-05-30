from collections import defaultdict
import json

from odoo import fields, http
from odoo.http import request


class RonixQualityInspectionController(http.Controller):

    def _get_period_label(self, report):
        month_label = dict(report.MONTH_SELECTION).get(report.report_month, '')
        week_label = dict(report.WEEK_SELECTION).get(report.report_week, '')
        return '%s %s - %s' % (month_label, report.report_year, week_label)

    @http.route('/kalite-denetim-raporu', type='http', auth='public', website=True, sitemap=False)
    def inspection_department_list(self, **_kwargs):
        departments = request.env['ronix.quality.inspection.department'].sudo().search([
            ('active', '=', True),
        ], order='sequence asc, name asc')
        reports = request.env['ronix.quality.inspection.report'].sudo().search([
            ('department_id', 'in', departments.ids),
            ('active', '=', True),
        ], order='report_year desc, report_month desc, report_week desc, id desc')

        reports_by_department = defaultdict(list)
        for report in reports:
            reports_by_department[report.department_id.id].append(report)

        department_cards = []
        for department in departments:
            department_reports = reports_by_department.get(department.id, [])
            report_count = len(department_reports)
            average_score = round(sum(report.score for report in department_reports) / report_count, 2) if report_count else 0.0
            latest_report = department_reports[0] if department_reports else False
            department_cards.append({
                'department': department,
                'report_count': report_count,
                'average_score': average_score,
                'latest_report': latest_report,
                'latest_period': self._get_period_label(latest_report) if latest_report else '',
            })

        return request.render('ronix_quality_manager.inspection_department_list_template', {
            'department_cards': department_cards,
        })

    @http.route('/kalite-denetim-raporu/<int:department_id>', type='http', auth='public', website=True, sitemap=False)
    def inspection_department_detail(self, department_id, **_kwargs):
        department = request.env['ronix.quality.inspection.department'].sudo().search([
            ('id', '=', department_id),
            ('active', '=', True),
        ], limit=1)
        if not department:
            return request.not_found()

        reports = request.env['ronix.quality.inspection.report'].sudo().search([
            ('department_id', '=', department.id),
            ('active', '=', True),
        ], order='report_year desc, report_month desc, report_week desc, id desc')

        month_groups = []
        grouped_reports = defaultdict(list)
        for report in reports:
            grouped_reports[(report.report_year, report.report_month)].append(report)

        month_label_map = dict(request.env['ronix.quality.inspection.report'].MONTH_SELECTION)
        for (year, month), month_reports in sorted(grouped_reports.items(), reverse=True):
            month_groups.append({
                'label': '%s %s' % (month_label_map.get(month, ''), year),
                'reports': [{
                    'report': report,
                    'period_label': self._get_period_label(report),
                    'good_lines': report.line_ids.filtered(lambda line: line.answer == 'yes'),
                    'bad_lines': report.line_ids.filtered(lambda line: line.answer == 'no'),
                } for report in month_reports],
            })

        all_lines = reports.mapped('line_ids')
        question_stats = []
        for question in department.question_ids.filtered('active').sorted(lambda q: (q.sequence, q.id)):
            lines = all_lines.filtered(
                lambda line, q=question: line.question_id.id == q.id
                or (not line.question_id and (line.question_text or '').strip() == (q.name or '').strip())
            )
            total = len(lines)
            yes_count = len(lines.filtered(lambda line: line.answer == 'yes'))
            no_count = total - yes_count
            success_rate = round((yes_count / total) * 100, 2) if total else 0.0
            recent_bad_periods = [self._get_period_label(line.report_id) for line in lines.filtered(lambda line: line.answer == 'no')[:3]]
            question_stats.append({
                'question': question,
                'total': total,
                'yes_count': yes_count,
                'no_count': no_count,
                'success_rate': success_rate,
                'recent_bad_periods': recent_bad_periods,
            })

        score_points = [{
            'label': self._get_period_label(report),
            'score': report.score,
        } for report in reports[:8]]

        return request.render('ronix_quality_manager.inspection_department_detail_template', {
            'department': department,
            'reports': reports,
            'month_groups': month_groups,
            'question_stats': question_stats,
            'score_points': score_points,
            'average_score': round(sum(reports.mapped('score')) / len(reports), 2) if reports else 0.0,
        })

    @http.route('/haftalik-kalite-denetim-formu', type='http', auth='user', website=True, sitemap=False)
    def inspection_frontend_form(self, success=None, **_kwargs):
        departments = request.env['ronix.quality.inspection.department'].search([
            ('active', '=', True),
        ], order='sequence asc, name asc')
        question_payload = {}
        for department in departments:
            question_payload[department.id] = [{
                'id': question.id,
                'sequence': question.sequence,
                'name': question.name,
                'weight': question.weight,
            } for question in department.question_ids.filtered('active').sorted(lambda q: (q.sequence, q.id))]
        return request.render('ronix_quality_manager.inspection_frontend_form_template', {
            'success': success,
            'departments': departments,
            'today_year': fields.Date.today().year,
            'current_month': '%02d' % fields.Date.today().month,
            'question_payload_json': json.dumps(question_payload),
            'month_selection': request.env['ronix.quality.inspection.report'].MONTH_SELECTION,
            'week_selection': request.env['ronix.quality.inspection.report'].WEEK_SELECTION,
        })

    @http.route('/haftalik-kalite-denetim-formu/submit', type='http', auth='user', website=True, methods=['POST'], sitemap=False)
    def inspection_frontend_form_submit(self, **post):
        request.env['ronix.quality.inspection.report'].create_or_update_frontend_report({
            'department_id': int(post.get('department_id') or 0),
            'report_year': int(post.get('report_year') or fields.Date.today().year),
            'report_month': post.get('report_month') or '%02d' % fields.Date.today().month,
            'report_week': post.get('report_week') or '01',
        }, post.get('line_payload'))
        return request.redirect('/haftalik-kalite-denetim-formu?success=1')
