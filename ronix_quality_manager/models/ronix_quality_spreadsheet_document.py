import base64
import io
import json
import posixpath
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


XML_NS = {
    'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}

CELL_REF_RE = re.compile(r'([A-Z]+)(\d+)')
INDEXED_COLORS = {
    0: '#000000',
    1: '#FFFFFF',
    2: '#FF0000',
    3: '#00FF00',
    4: '#0000FF',
    5: '#FFFF00',
    6: '#FF00FF',
    7: '#00FFFF',
    8: '#000000',
    9: '#FFFFFF',
    10: '#FF0000',
    11: '#00FF00',
    12: '#0000FF',
    13: '#FFFF00',
    14: '#FF00FF',
    15: '#00FFFF',
    16: '#800000',
    17: '#008000',
    18: '#000080',
    19: '#808000',
    20: '#800080',
    21: '#008080',
    22: '#C0C0C0',
    23: '#808080',
    24: '#9999FF',
    25: '#993366',
    26: '#FFFFCC',
    27: '#CCFFFF',
    28: '#660066',
    29: '#FF8080',
    30: '#0066CC',
    31: '#CCCCFF',
    32: '#000080',
    33: '#FF00FF',
    34: '#FFFF00',
    35: '#00FFFF',
    36: '#800080',
    37: '#800000',
    38: '#008080',
    39: '#0000FF',
    40: '#00CCFF',
    41: '#CCFFFF',
    42: '#CCFFCC',
    43: '#FFFF99',
    44: '#99CCFF',
    45: '#FF99CC',
    46: '#CC99FF',
    47: '#FFCC99',
    48: '#3366FF',
    49: '#33CCCC',
    50: '#99CC00',
    51: '#FFCC00',
    52: '#FF9900',
    53: '#FF6600',
    54: '#666699',
    55: '#969696',
    56: '#003366',
    57: '#339966',
    58: '#003300',
    59: '#333300',
    60: '#993300',
    61: '#993366',
    62: '#333399',
    63: '#333333',
}


class RonixQualitySpreadsheetDocument(models.Model):
    _name = 'ronix.quality.spreadsheet.document'
    _description = 'Ronix Quality Spreadsheet Document'
    _order = 'write_date desc, id desc'

    name = fields.Char(required=True)
    upload_file = fields.Binary(string='Excel File', attachment=True, required=True)
    upload_filename = fields.Char(string='Filename', required=True)
    google_sheets_url = fields.Char(string='Google Sheets URL')
    sheet_data_json = fields.Text(string='Workbook Data', readonly=True)
    access_token = fields.Char(string='Access Token', readonly=True, copy=False, index=True)
    sheet_count = fields.Integer(compute='_compute_workbook_stats')
    row_count = fields.Integer(compute='_compute_workbook_stats')
    editor_url = fields.Char(string='Editor URL', compute='_compute_urls')
    download_url = fields.Char(string='Download URL', compute='_compute_urls')
    last_saved_on = fields.Datetime(readonly=True, copy=False)
    active = fields.Boolean(default=True)

    @api.depends('sheet_data_json')
    def _compute_workbook_stats(self):
        for record in self:
            workbook = record._get_workbook_data()
            sheets = workbook.get('sheets', [])
            record.sheet_count = len(sheets)
            record.row_count = sum(len(sheet.get('rows', [])) for sheet in sheets)

    @api.depends('access_token')
    def _compute_urls(self):
        for record in self:
            if record.access_token:
                record.editor_url = '/ronix-quality/spreadsheet/%s' % record.access_token
                record.download_url = '/ronix-quality/spreadsheet/%s/download' % record.access_token
            else:
                record.editor_url = False
                record.download_url = False

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = [self._prepare_workbook_vals(vals) for vals in vals_list]
        return super().create(prepared_vals_list)

    def write(self, vals):
        prepared_vals = self._prepare_workbook_vals(vals)
        return super().write(prepared_vals)

    def action_open_editor(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.editor_url,
            'target': 'new',
        }

    def action_download_workbook(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.download_url,
            'target': 'new',
        }

    def action_open_google_sheets(self):
        self.ensure_one()
        if not self.google_sheets_url:
            raise UserError('Google Sheets linki bulunamadi.')
        return {
            'type': 'ir.actions.act_url',
            'url': self.google_sheets_url,
            'target': 'new',
        }

    def action_reparse_workbook(self):
        for record in self:
            if not record.upload_file:
                raise UserError('Excel dosyasi bulunamadi.')
            workbook = record._parse_xlsx_binary(base64.b64decode(record.upload_file))
            record.write({
                'sheet_data_json': json.dumps(workbook, ensure_ascii=False),
                'last_saved_on': fields.Datetime.now(),
            })

    def _prepare_workbook_vals(self, vals):
        prepared_vals = dict(vals)
        if not prepared_vals.get('access_token'):
            prepared_vals['access_token'] = uuid.uuid4().hex
        if prepared_vals.get('upload_file'):
            filename = prepared_vals.get('upload_filename') or self.upload_filename or 'workbook.xlsx'
            if not filename.lower().endswith('.xlsx'):
                raise ValidationError('Yalnizca .xlsx dosyalari desteklenir.')
            if not self.env.context.get('skip_spreadsheet_parse'):
                binary_data = base64.b64decode(prepared_vals['upload_file'])
                workbook = self._parse_xlsx_binary(binary_data)
                prepared_vals['sheet_data_json'] = json.dumps(workbook, ensure_ascii=False)
                prepared_vals['last_saved_on'] = fields.Datetime.now()
            if not prepared_vals.get('name'):
                prepared_vals['name'] = filename.rsplit('.', 1)[0]
        return prepared_vals

    def _get_workbook_data(self):
        self.ensure_one()
        if not self.sheet_data_json:
            return {'sheets': []}
        try:
            return json.loads(self.sheet_data_json)
        except json.JSONDecodeError:
            return {'sheets': []}

    def _parse_xlsx_binary(self, binary_data):
        try:
            archive = zipfile.ZipFile(io.BytesIO(binary_data))
        except zipfile.BadZipFile as exc:
            raise ValidationError('Gecersiz .xlsx dosyasi.') from exc

        if 'xl/workbook.xml' not in archive.namelist():
            raise ValidationError('Gecersiz .xlsx dosyasi. Excel 2007+ formatinda bir .xlsx dosyasi yukleyin.')

        shared_strings = self._read_shared_strings(archive)
        style_payload = self._read_styles_payload(archive)
        workbook_root = ET.fromstring(archive.read('xl/workbook.xml'))
        workbook_rels = self._read_workbook_rels(archive)
        sheets = []
        for sheet_node in workbook_root.findall('main:sheets/main:sheet', XML_NS):
            rel_id = sheet_node.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            sheet_name = sheet_node.attrib.get('name') or 'Sheet'
            sheet_path = workbook_rels.get(rel_id)
            if not sheet_path:
                continue
            sheet_xml = archive.read(sheet_path)
            sheet_data = self._read_sheet_payload(sheet_xml, shared_strings, style_payload.get('style_map', []))
            sheets.append({
                'name': sheet_name,
                'rows': sheet_data['rows'],
                'merges': sheet_data['merges'],
                'col_widths': sheet_data['col_widths'],
                'row_heights': sheet_data['row_heights'],
            })
        if not sheets:
            raise ValidationError('Excel dosyasinda okunabilir sayfa bulunamadi.')
        return {
            'sheets': sheets,
            'style_map': style_payload.get('style_map', []),
            'styles_xml': style_payload.get('styles_xml', ''),
        }

    def _read_shared_strings(self, archive):
        if 'xl/sharedStrings.xml' not in archive.namelist():
            return []
        root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        strings = []
        for string_item in root.findall('main:si', XML_NS):
            text_parts = []
            for text_node in string_item.findall('.//main:t', XML_NS):
                text_parts.append(text_node.text or '')
            strings.append(''.join(text_parts))
        return strings

    def _read_workbook_rels(self, archive):
        rels_path = 'xl/_rels/workbook.xml.rels'
        if rels_path not in archive.namelist():
            return {}
        root = ET.fromstring(archive.read(rels_path))
        rels = {}
        for rel_node in root.findall('rel:Relationship', XML_NS):
            target = rel_node.attrib.get('Target', '')
            if not target:
                continue
            rels[rel_node.attrib.get('Id')] = posixpath.normpath(posixpath.join('xl', target))
        return rels

    def _read_styles_payload(self, archive):
        styles_xml = ''
        style_map = []
        theme_colors = self._read_theme_colors(archive)
        if 'xl/styles.xml' in archive.namelist():
            styles_xml = archive.read('xl/styles.xml').decode('utf-8')
            style_map = self._parse_styles_xml(styles_xml, theme_colors)
        return {
            'styles_xml': styles_xml,
            'style_map': style_map,
        }

    def _parse_styles_xml(self, styles_xml, theme_colors):
        if not styles_xml:
            return []
        root = ET.fromstring(styles_xml)
        fonts = root.find('main:fonts', XML_NS)
        fills = root.find('main:fills', XML_NS)
        borders = root.find('main:borders', XML_NS)
        cell_xfs = root.find('main:cellXfs', XML_NS)

        font_payloads = [self._parse_font_payload(node, theme_colors) for node in fonts.findall('main:font', XML_NS)] if fonts is not None else []
        fill_payloads = [self._parse_fill_payload(node, theme_colors) for node in fills.findall('main:fill', XML_NS)] if fills is not None else []
        border_payloads = [self._parse_border_payload(node, theme_colors) for node in borders.findall('main:border', XML_NS)] if borders is not None else []

        style_map = []
        if cell_xfs is not None:
            for xf_node in cell_xfs.findall('main:xf', XML_NS):
                style_map.append(self._parse_xf_payload(xf_node, font_payloads, fill_payloads, border_payloads))
        return style_map

    def _parse_font_payload(self, font_node, theme_colors):
        return {
            'bold': font_node.find('main:b', XML_NS) is not None,
            'italic': font_node.find('main:i', XML_NS) is not None,
            'size': self._node_attr(font_node.find('main:sz', XML_NS), 'val'),
            'color': self._read_color(font_node.find('main:color', XML_NS), theme_colors),
        }

    def _parse_fill_payload(self, fill_node, theme_colors):
        pattern = fill_node.find('main:patternFill', XML_NS)
        if pattern is None:
            return {}
        fg_color = self._read_color(pattern.find('main:fgColor', XML_NS), theme_colors)
        bg_color = self._read_color(pattern.find('main:bgColor', XML_NS), theme_colors)
        return {
            'foreground': fg_color,
            'background': bg_color,
            'pattern': pattern.attrib.get('patternType'),
        }

    def _parse_border_payload(self, border_node, theme_colors):
        payload = {}
        for side_name in ('left', 'right', 'top', 'bottom'):
            side_node = border_node.find(f'main:{side_name}', XML_NS)
            if side_node is None:
                continue
            payload[side_name] = {
                'style': side_node.attrib.get('style'),
                'color': self._read_color(side_node.find('main:color', XML_NS), theme_colors) or '#000000',
            }
        return payload

    def _parse_xf_payload(self, xf_node, font_payloads, fill_payloads, border_payloads):
        font_index = int(xf_node.attrib.get('fontId', 0) or 0)
        fill_index = int(xf_node.attrib.get('fillId', 0) or 0)
        border_index = int(xf_node.attrib.get('borderId', 0) or 0)
        alignment_node = xf_node.find('main:alignment', XML_NS)
        return {
            'font': font_payloads[font_index] if font_index < len(font_payloads) else {},
            'fill': fill_payloads[fill_index] if fill_index < len(fill_payloads) else {},
            'border': border_payloads[border_index] if border_index < len(border_payloads) else {},
            'alignment': {
                'horizontal': alignment_node.attrib.get('horizontal') if alignment_node is not None else '',
                'vertical': alignment_node.attrib.get('vertical') if alignment_node is not None else '',
                'wrap_text': alignment_node.attrib.get('wrapText') == '1' if alignment_node is not None else False,
            },
            'css': self._build_style_css(
                font_payloads[font_index] if font_index < len(font_payloads) else {},
                fill_payloads[fill_index] if fill_index < len(fill_payloads) else {},
                border_payloads[border_index] if border_index < len(border_payloads) else {},
                alignment_node,
            ),
        }

    def _build_style_css(self, font_payload, fill_payload, border_payload, alignment_node):
        css = {}
        if font_payload.get('bold'):
            css['font-weight'] = '700'
        if font_payload.get('italic'):
            css['font-style'] = 'italic'
        if font_payload.get('size'):
            css['font-size'] = '%spt' % font_payload['size']
        if font_payload.get('color'):
            css['color'] = font_payload['color']
        if fill_payload.get('foreground') and fill_payload.get('pattern') not in ('none', 'gray125'):
            css['background-color'] = fill_payload['foreground']
        if alignment_node is not None:
            if alignment_node.attrib.get('horizontal'):
                css['text-align'] = alignment_node.attrib.get('horizontal')
            if alignment_node.attrib.get('vertical'):
                css['vertical-align'] = alignment_node.attrib.get('vertical')
            if alignment_node.attrib.get('wrapText') == '1':
                css['white-space'] = 'pre-wrap'
        for side_name, css_name in (
            ('left', 'border-left'),
            ('right', 'border-right'),
            ('top', 'border-top'),
            ('bottom', 'border-bottom'),
        ):
            side_payload = border_payload.get(side_name) or {}
            if side_payload.get('style'):
                css[css_name] = '1px solid %s' % (side_payload.get('color') or '#000000')
        return css

    def _read_sheet_payload(self, sheet_xml, shared_strings, style_map):
        root = ET.fromstring(sheet_xml)
        row_map = {}
        max_col_index = 0
        col_widths = {}
        row_heights = {}
        merges = []

        cols_node = root.find('main:cols', XML_NS)
        if cols_node is not None:
            for col_node in cols_node.findall('main:col', XML_NS):
                min_col = int(col_node.attrib.get('min', 1))
                max_col = int(col_node.attrib.get('max', min_col))
                width = col_node.attrib.get('width')
                if not width:
                    continue
                for col_index in range(min_col, max_col + 1):
                    col_widths[str(col_index)] = float(width)

        for row_node in root.findall('main:sheetData/main:row', XML_NS):
            row_index = int(row_node.attrib.get('r', len(row_map) + 1))
            if row_node.attrib.get('ht'):
                row_heights[str(row_index)] = float(row_node.attrib.get('ht'))
            row_values = row_map.setdefault(row_index, {})
            for cell_node in row_node.findall('main:c', XML_NS):
                ref = cell_node.attrib.get('r', '')
                col_index, _row_index = self._cell_ref_to_indices(ref)
                max_col_index = max(max_col_index, col_index)
                row_values[col_index] = {
                    'value': self._read_cell_value(cell_node, shared_strings),
                    'style': int(cell_node.attrib.get('s', 0) or 0),
                }

        merge_nodes = root.find('main:mergeCells', XML_NS)
        if merge_nodes is not None:
            for merge_node in merge_nodes.findall('main:mergeCell', XML_NS):
                merge_ref = merge_node.attrib.get('ref')
                if not merge_ref or ':' not in merge_ref:
                    continue
                start_ref, end_ref = merge_ref.split(':', 1)
                start_col, start_row = self._cell_ref_to_indices(start_ref)
                end_col, end_row = self._cell_ref_to_indices(end_ref)
                merges.append({
                    'row': start_row,
                    'col': start_col,
                    'rowspan': (end_row - start_row) + 1,
                    'colspan': (end_col - start_col) + 1,
                })
                max_col_index = max(max_col_index, end_col)

        if not row_map:
            return {
                'rows': [[{'value': '', 'style': 0}]],
                'merges': merges,
                'col_widths': col_widths,
                'row_heights': row_heights,
            }

        rows = []
        max_row_index = max(row_map)
        for row_index in range(1, max_row_index + 1):
            row_values = row_map.get(row_index, {})
            row = [row_values.get(col_index, {'value': '', 'style': 0}) for col_index in range(1, max_col_index + 1)]
            while row and row[-1].get('value') == '' and row[-1].get('style', 0) == 0:
                row.pop()
            rows.append(row)
        while rows and all(cell.get('value') == '' and cell.get('style', 0) == 0 for cell in rows[-1]):
            rows.pop()
        return {
            'rows': rows or [[{'value': '', 'style': 0}]],
            'merges': merges,
            'col_widths': col_widths,
            'row_heights': row_heights,
        }

    def _read_cell_value(self, cell_node, shared_strings):
        cell_type = cell_node.attrib.get('t')
        value_node = cell_node.find('main:v', XML_NS)
        inline_node = cell_node.find('main:is/main:t', XML_NS)

        if cell_type == 'inlineStr':
            return inline_node.text if inline_node is not None and inline_node.text is not None else ''
        if cell_type == 's':
            if value_node is None or value_node.text is None:
                return ''
            index = int(value_node.text)
            return shared_strings[index] if index < len(shared_strings) else ''
        if cell_type == 'b':
            return 'TRUE' if value_node is not None and value_node.text == '1' else 'FALSE'
        if value_node is None or value_node.text is None:
            return ''
        return value_node.text

    def _cell_ref_to_indices(self, cell_ref):
        match = CELL_REF_RE.fullmatch(cell_ref or '')
        if not match:
            return 1, 1
        column_letters, row_digits = match.groups()
        col_index = 0
        for char in column_letters:
            col_index = (col_index * 26) + (ord(char) - 64)
        return col_index, int(row_digits)

    def export_workbook_binary(self):
        self.ensure_one()
        workbook = self._get_workbook_data()
        sheets = workbook.get('sheets', []) or [{'name': 'Sheet1', 'rows': [[]]}]
        styles_xml = workbook.get('styles_xml') or self._build_styles_xml()
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('[Content_Types].xml', self._build_content_types_xml(len(sheets)))
            archive.writestr('_rels/.rels', self._build_root_rels_xml())
            archive.writestr('xl/workbook.xml', self._build_workbook_xml(sheets))
            archive.writestr('xl/_rels/workbook.xml.rels', self._build_workbook_rels_xml(sheets))
            archive.writestr('xl/styles.xml', styles_xml)
            for index, sheet in enumerate(sheets, start=1):
                archive.writestr(
                    'xl/worksheets/sheet%s.xml' % index,
                    self._build_sheet_xml(sheet),
                )
        memory.seek(0)
        return memory.read()

    def _build_content_types_xml(self, sheet_count):
        overrides = [
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        ]
        for index in range(1, sheet_count + 1):
            overrides.append(
                '<Override PartName="/xl/worksheets/sheet%s.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                % index
            )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            + ''.join(overrides)
            + '</Types>'
        )

    def _build_root_rels_xml(self):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            '</Relationships>'
        )

    def _build_workbook_xml(self, sheets):
        sheet_nodes = []
        for index, sheet in enumerate(sheets, start=1):
            sheet_name = self._xml_escape(sheet.get('name') or 'Sheet%s' % index)
            sheet_nodes.append(
                '<sheet name="%s" sheetId="%s" r:id="rId%s"/>'
                % (sheet_name, index, index)
            )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets>%s</sheets>'
            '</workbook>'
        ) % ''.join(sheet_nodes)

    def _build_workbook_rels_xml(self, sheets):
        rel_nodes = []
        for index, _sheet in enumerate(sheets, start=1):
            rel_nodes.append(
                '<Relationship Id="rId%s" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                'Target="worksheets/sheet%s.xml"/>'
                % (index, index)
            )
        rel_nodes.append(
            '<Relationship Id="rId%s" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
            'Target="styles.xml"/>'
            % (len(sheets) + 1)
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'
        ) % ''.join(rel_nodes)

    def _build_styles_xml(self):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
            '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
            '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
            '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
            '</styleSheet>'
        )

    def _build_sheet_xml(self, sheet):
        rows = sheet.get('rows', [])
        merges = sheet.get('merges', [])
        col_widths = sheet.get('col_widths', {})
        row_heights = sheet.get('row_heights', {})
        normalized_rows = self._normalize_sheet_rows(rows)
        row_nodes = []
        max_col_count = max((len(row) for row in normalized_rows), default=1)
        for row_index, row in enumerate(normalized_rows, start=1):
            cells = []
            row_attrs = ['r="%s"' % row_index]
            row_height = row_heights.get(str(row_index))
            if row_height:
                row_attrs.append('ht="%s"' % row_height)
                row_attrs.append('customHeight="1"')
            for col_index, cell in enumerate(row, start=1):
                value = cell.get('value')
                if value in (None, '') and int(cell.get('style', 0) or 0) == 0:
                    continue
                cell_ref = '%s%s' % (self._column_name(col_index), row_index)
                cells.append(self._build_cell_xml(cell_ref, cell))
            row_nodes.append('<row %s>%s</row>' % (' '.join(row_attrs), ''.join(cells)))
        max_row = max(len(normalized_rows), max((merge['row'] + merge['rowspan'] - 1 for merge in merges), default=1), 1)
        max_col = max(max_col_count, max((merge['col'] + merge['colspan'] - 1 for merge in merges), default=1), 1)
        dimension_ref = 'A1:%s%s' % (self._column_name(max_col), max_row)
        cols_xml = self._build_cols_xml(col_widths)
        merge_xml = self._build_merges_xml(merges)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<dimension ref="%s"/>'
            '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
            '<sheetFormatPr defaultRowHeight="15"/>'
            '%s'
            '<sheetData>%s</sheetData>'
            '%s'
            '</worksheet>'
        ) % (dimension_ref, cols_xml, ''.join(row_nodes), merge_xml)

    def _build_cell_xml(self, cell_ref, cell):
        value = cell.get('value')
        style_index = int(cell.get('style', 0) or 0)
        string_value = '' if value is None else str(value)
        upper_value = string_value.upper()
        style_attr = ' s="%s"' % style_index if style_index else ''
        if upper_value in ('TRUE', 'FALSE'):
            return '<c r="%s"%s t="b"><v>%s</v></c>' % (cell_ref, style_attr, '1' if upper_value == 'TRUE' else '0')
        if self._is_number(string_value):
            return '<c r="%s"%s><v>%s</v></c>' % (cell_ref, style_attr, self._xml_escape(string_value))
        return '<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (
            cell_ref,
            style_attr,
            self._xml_escape(string_value),
        )

    def _normalize_sheet_rows(self, rows):
        normalized_rows = rows or []
        if not normalized_rows:
            return [[{'value': '', 'style': 0}]]
        result = []
        for row in normalized_rows:
            normalized_row = []
            for cell in row:
                if isinstance(cell, dict):
                    normalized_row.append({
                        'value': cell.get('value', ''),
                        'style': int(cell.get('style', 0) or 0),
                    })
                else:
                    normalized_row.append({'value': cell or '', 'style': 0})
            result.append(normalized_row)
        return result

    def _build_cols_xml(self, col_widths):
        if not col_widths:
            return ''
        col_nodes = []
        for col_index in sorted((int(key) for key in col_widths.keys())):
            width = col_widths.get(str(col_index))
            if not width:
                continue
            col_nodes.append('<col min="%s" max="%s" width="%s" customWidth="1"/>' % (col_index, col_index, width))
        return '<cols>%s</cols>' % ''.join(col_nodes) if col_nodes else ''

    def _build_merges_xml(self, merges):
        if not merges:
            return ''
        merge_nodes = []
        for merge in merges:
            start_ref = '%s%s' % (self._column_name(merge['col']), merge['row'])
            end_ref = '%s%s' % (
                self._column_name(merge['col'] + merge['colspan'] - 1),
                merge['row'] + merge['rowspan'] - 1,
            )
            merge_nodes.append('<mergeCell ref="%s:%s"/>' % (start_ref, end_ref))
        return '<mergeCells count="%s">%s</mergeCells>' % (len(merge_nodes), ''.join(merge_nodes))

    def _column_name(self, col_index):
        letters = []
        while col_index:
            col_index, remainder = divmod(col_index - 1, 26)
            letters.append(chr(65 + remainder))
        return ''.join(reversed(letters)) or 'A'

    def _is_number(self, value):
        try:
            float(value)
        except (TypeError, ValueError):
            return False
        return value not in ('', None)

    def _xml_escape(self, value):
        return (
            str(value)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;')
        )

    def _read_theme_colors(self, archive):
        theme_path = 'xl/theme/theme1.xml'
        if theme_path not in archive.namelist():
            return []
        root = ET.fromstring(archive.read(theme_path))
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        clr_scheme = root.find('.//a:clrScheme', ns)
        if clr_scheme is None:
            return []
        theme_colors = []
        for child in list(clr_scheme):
            color_value = None
            srgb = child.find('a:srgbClr', ns)
            sys = child.find('a:sysClr', ns)
            if srgb is not None:
                color_value = '#%s' % srgb.attrib.get('val', '')[-6:]
            elif sys is not None:
                color_value = '#%s' % sys.attrib.get('lastClr', '')[-6:]
            theme_colors.append(color_value)
        return theme_colors

    def _read_color(self, color_node, theme_colors=None):
        if color_node is None:
            return None
        if color_node.attrib.get('auto') == '1':
            return None
        rgb = color_node.attrib.get('rgb')
        if rgb:
            rgb = rgb[-6:]
            return '#%s' % rgb
        indexed = color_node.attrib.get('indexed')
        if indexed is not None:
            indexed_value = int(indexed)
            if indexed_value in (64, 65):
                return None
            return INDEXED_COLORS.get(indexed_value)
        theme = color_node.attrib.get('theme')
        if theme is not None:
            base_color = None
            theme_index = int(theme)
            if theme_colors and theme_index < len(theme_colors):
                base_color = theme_colors[theme_index]
            if base_color:
                tint = color_node.attrib.get('tint')
                if tint is not None:
                    return self._apply_tint(base_color, float(tint))
                return base_color
        return None

    def _apply_tint(self, hex_color, tint):
        hex_color = (hex_color or '').lstrip('#')
        if len(hex_color) != 6:
            return '#%s' % hex_color if hex_color else None
        red = int(hex_color[0:2], 16)
        green = int(hex_color[2:4], 16)
        blue = int(hex_color[4:6], 16)
        return '#%02X%02X%02X' % (
            self._tint_channel(red, tint),
            self._tint_channel(green, tint),
            self._tint_channel(blue, tint),
        )

    def _tint_channel(self, value, tint):
        if tint < 0:
            return max(0, min(255, round(value * (1.0 + tint))))
        return max(0, min(255, round(value + ((255 - value) * tint))))

    def _node_attr(self, node, attr_name):
        return node.attrib.get(attr_name) if node is not None else None
