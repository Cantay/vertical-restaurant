import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RonixQualityInspectionDepartment(models.Model):
    _name = 'ronix.quality.inspection.department'
    _description = 'Ronix Quality Inspection Department'
    _order = 'sequence asc, name asc'

    name = fields.Char(string='Departman', required=True)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    question_ids = fields.One2many('ronix.quality.inspection.question', 'department_id', string='Sorular')
    report_ids = fields.One2many('ronix.quality.inspection.report', 'department_id', string='Raporlar')
    question_count = fields.Integer(compute='_compute_counts')
    report_count = fields.Integer(compute='_compute_counts')

    _sql_constraints = [
        (
            'ronix_quality_inspection_department_name_location_unique',
            'unique(name, location_id)',
            'Ayni lokasyonda departman adi benzersiz olmalidir.',
        ),
    ]

    @api.depends('question_ids', 'report_ids')
    def _compute_counts(self):
        for record in self:
            record.question_count = len(record.question_ids)
            record.report_count = len(record.report_ids)


class RonixQualityInspectionQuestion(models.Model):
    _name = 'ronix.quality.inspection.question'
    _description = 'Ronix Quality Inspection Question'
    _order = 'department_id, sequence asc, id asc'

    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        related='department_id.location_id',
        store=True,
        readonly=True,
    )
    department_id = fields.Many2one(
        'ronix.quality.inspection.department',
        string='Departman',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Soru', required=True)
    weight = fields.Float(string='Puan Agirligi', required=True, default=4.0, digits=(16, 2))
    active = fields.Boolean(default=True)

    @api.constrains('weight')
    def _check_weight(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError('Puan agirligi sifirdan buyuk olmalidir.')


class RonixQualityInspectionReport(models.Model):
    _name = 'ronix.quality.inspection.report'
    _description = 'Ronix Quality Inspection Report'
    _order = 'report_year desc, report_month desc, report_week desc, department_id asc, id desc'

    MONTH_SELECTION = [
        ('01', 'Ocak'),
        ('02', 'Subat'),
        ('03', 'Mart'),
        ('04', 'Nisan'),
        ('05', 'Mayis'),
        ('06', 'Haziran'),
        ('07', 'Temmuz'),
        ('08', 'Agustos'),
        ('09', 'Eylul'),
        ('10', 'Ekim'),
        ('11', 'Kasim'),
        ('12', 'Aralik'),
    ]
    WEEK_SELECTION = [
        ('01', '1. Hafta'),
        ('02', '2. Hafta'),
        ('03', '3. Hafta'),
        ('04', '4. Hafta'),
        ('05', '5. Hafta'),
    ]

    name = fields.Char(compute='_compute_name', store=True)
    location_id = fields.Many2one(
        'ronix.quality.location',
        string='Lokasyon',
        default=lambda self: self.env['ronix.quality.location']._get_single_active_location_id(),
    )
    department_id = fields.Many2one(
        'ronix.quality.inspection.department',
        string='Departman',
        required=True,
        ondelete='restrict',
        index=True,
    )
    report_year = fields.Integer(string='Yil', required=True, default=lambda self: fields.Date.today().year)
    report_month = fields.Selection(MONTH_SELECTION, string='Ay', required=True, default=lambda self: '%02d' % fields.Date.today().month)
    report_week = fields.Selection(WEEK_SELECTION, string='Hafta', required=True, default='01')
    line_ids = fields.One2many(
        'ronix.quality.inspection.report.line',
        'report_id',
        string='Cevaplar',
        copy=True,
    )
    total_weight = fields.Float(string='Toplam Puan', compute='_compute_scores', store=True, digits=(16, 2))
    achieved_weight = fields.Float(string='Alinan Puan', compute='_compute_scores', store=True, digits=(16, 2))
    score = fields.Float(string='100 Uzerinden Puan', compute='_compute_scores', store=True, digits=(16, 2))
    answer_count = fields.Integer(string='Cevaplanan Soru', compute='_compute_scores', store=True)
    question_count = fields.Integer(string='Soru Sayisi', compute='_compute_scores', store=True)
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'ronix_quality_inspection_report_unique_period',
            'unique(department_id, report_year, report_month, report_week)',
            'Ayni departman icin ayni yil, ay ve hafta kombinasyonunda yalnizca bir rapor olabilir.',
        ),
    ]

    @api.depends('department_id', 'report_year', 'report_month', 'report_week')
    def _compute_name(self):
        month_map = dict(self.MONTH_SELECTION)
        week_map = dict(self.WEEK_SELECTION)
        for record in self:
            month_label = month_map.get(record.report_month, '')
            week_label = week_map.get(record.report_week, '')
            department_name = record.department_id.name or ''
            record.name = '%s - %s %s - %s' % (department_name, month_label, record.report_year or '', week_label)

    def _compute_website_url(self):
        for record in self:
            record.website_url = '/haftalik-kalite-denetim-formu'

    @api.depends('line_ids.weight', 'line_ids.answer', 'line_ids.achieved_weight')
    def _compute_scores(self):
        for record in self:
            total_weight = sum(record.line_ids.mapped('weight'))
            achieved_weight = sum(record.line_ids.mapped('achieved_weight'))
            answer_count = len(record.line_ids.filtered('answer'))
            question_count = len(record.line_ids)
            record.total_weight = total_weight
            record.achieved_weight = achieved_weight
            record.answer_count = answer_count
            record.question_count = question_count
            record.score = round((achieved_weight / total_weight) * 100, 2) if total_weight else 0.0

    @api.onchange('department_id')
    def _onchange_department_id(self):
        for record in self:
            record.line_ids = record._build_question_line_commands()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('department_id') and not vals.get('line_ids'):
                department = self.env['ronix.quality.inspection.department'].browse(vals['department_id'])
                vals['line_ids'] = department._build_question_line_commands()
        return super().create(vals_list)

    def action_refresh_questions(self):
        for record in self:
            record.line_ids = record._build_question_line_commands()

    def action_open_website_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'new',
        }

    def _build_question_line_commands(self):
        self.ensure_one()
        if not self.department_id or not self.department_id.exists():
            return [fields.Command.clear()]
        return self.department_id._build_question_line_commands()

    @api.constrains('line_ids')
    def _check_lines_answered(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError('Rapor icin en az bir soru bulunmalidir.')
            unanswered_lines = record.line_ids.filtered(lambda line: not line.answer)
            if unanswered_lines:
                raise ValidationError('Tum sorular icin Uygun veya Uygun Degil secimi yapilmalidir.')

    @api.model
    def create_or_update_frontend_report(self, values, payload):
        department = self.env['ronix.quality.inspection.department'].browse(values.get('department_id'))
        if not department.exists():
            raise ValidationError('Gecerli bir departman secilmelidir.')
        line_commands = self.env['ronix.quality.inspection.report.line'].prepare_frontend_commands(payload, department)
        search_domain = [
            ('department_id', '=', department.id),
            ('report_year', '=', values.get('report_year')),
            ('report_month', '=', values.get('report_month')),
            ('report_week', '=', values.get('report_week')),
        ]
        report = self.search(search_domain, limit=1)
        report_values = {
            'location_id': department.location_id.id or False,
            'department_id': department.id,
            'report_year': values.get('report_year'),
            'report_month': values.get('report_month'),
            'report_week': values.get('report_week'),
            'line_ids': line_commands,
            'active': True,
        }
        if report:
            report.write(report_values)
            return report
        return self.create(report_values)


class RonixQualityInspectionReportLine(models.Model):
    _name = 'ronix.quality.inspection.report.line'
    _description = 'Ronix Quality Inspection Report Line'
    _order = 'sequence asc, id asc'

    ANSWER_SELECTION = [
        ('yes', 'Uygun'),
        ('no', 'Uygun Degil'),
    ]

    report_id = fields.Many2one(
        'ronix.quality.inspection.report',
        string='Rapor',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    question_id = fields.Many2one(
        'ronix.quality.inspection.question',
        string='Kaynak Soru',
        ondelete='set null',
        readonly=True,
    )
    question_text = fields.Char(string='Soru', required=True)
    weight = fields.Float(string='Puan Agirligi', required=True, digits=(16, 2))
    answer = fields.Selection(ANSWER_SELECTION, string='Sonuc', required=True)
    achieved_weight = fields.Float(string='Alinan Puan', compute='_compute_achieved_weight', store=True, digits=(16, 2))

    @api.depends('weight', 'answer')
    def _compute_achieved_weight(self):
        for record in self:
            record.achieved_weight = record.weight if record.answer == 'yes' else 0.0

    @api.constrains('weight')
    def _check_weight(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError('Puan agirligi sifirdan buyuk olmalidir.')

    @api.model
    def prepare_frontend_commands(self, payload, department):
        try:
            rows = json.loads(payload or '[]')
        except json.JSONDecodeError:
            rows = []
        row_map = {
            int(row.get('question_id')): row
            for row in rows
            if isinstance(row, dict) and row.get('question_id')
        }
        commands = [fields.Command.clear()]
        for question in department.question_ids.filtered('active').sorted(lambda q: (q.sequence, q.id)):
            row = row_map.get(question.id, {})
            answer = row.get('answer')
            if answer not in dict(self.ANSWER_SELECTION):
                continue
            commands.append(fields.Command.create({
                'sequence': question.sequence,
                'question_id': question.id,
                'question_text': question.name,
                'weight': question.weight or 4.0,
                'answer': answer,
            }))
        if len(commands) == 1:
            raise ValidationError('Tum sorular icin Uygun veya Uygun Degil secimi yapilmalidir.')
        return commands


def _department_build_question_line_commands(self):
    if not self:
        return [fields.Command.clear()]
    self.ensure_one()
    return [fields.Command.clear()] + [
        fields.Command.create({
            'sequence': question.sequence,
            'question_id': question.id,
            'question_text': question.name,
            'weight': question.weight or 4.0,
        })
        for question in self.question_ids.filtered('active').sorted(lambda q: (q.sequence, q.id))
    ]


RonixQualityInspectionDepartment._build_question_line_commands = _department_build_question_line_commands
