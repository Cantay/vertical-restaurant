/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualitySpreadsheetEditor = publicWidget.Widget.extend({
    selector: ".s_ham_spreadsheet_editor",
    events: {
        "click .ham-sheet-save": "_onSave",
        "click .ham-sheet-add-row": "_onAddRow",
        "click .ham-sheet-add-col": "_onAddColumn",
        "click .ham-sheet-tab": "_onSelectSheet",
        "input .ham-sheet-cell": "_onCellInput",
    },

    async start() {
        this.state = {
            workbook: { sheets: [], style_map: [] },
            currentSheetIndex: 0,
            dirty: false,
        };
        this.tabsEl = this.el.querySelector(".ham-sheet-tabs");
        this.gridEl = this.el.querySelector(".ham-sheet-grid");
        this.statusEl = this.el.querySelector(".ham-sheet-status-text");
        await this._loadWorkbook();
        return publicWidget.Widget.prototype.start.call(this);
    },

    async _loadWorkbook() {
        this._setStatus("Yukleniyor...");
        const response = await fetch(this.el.dataset.loadUrl, {
            method: "GET",
            headers: { Accept: "application/json" },
        });
        const payload = await response.json();
        if (!payload.success) {
            this._setStatus(payload.error || "Dosya yuklenemedi.");
            return;
        }
        this.state.workbook = payload.document.workbook || { sheets: [] };
        if (!this.state.workbook.sheets.length) {
            this.state.workbook.sheets = [{ name: "Sheet1", rows: [[{ value: "", style: 0 }]], merges: [], col_widths: {}, row_heights: {} }];
        }
        this._render();
        this._setStatus(payload.document.last_saved_on ? `Son kayit: ${payload.document.last_saved_on}` : "Hazir");
    },

    _render() {
        this._renderTabs();
        this._renderGrid();
    },

    _renderTabs() {
        this.tabsEl.innerHTML = "";
        this.state.workbook.sheets.forEach((sheet, index) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `ham-sheet-tab${index === this.state.currentSheetIndex ? " is-active" : ""}`;
            button.dataset.sheetIndex = String(index);
            button.textContent = sheet.name || `Sheet ${index + 1}`;
            this.tabsEl.appendChild(button);
        });
    },

    _renderGrid() {
        const sheet = this._getCurrentSheet();
        const rows = this._normalizeRows(sheet.rows);
        const merges = sheet.merges || [];
        const colCount = Math.max(
            rows.reduce((max, row) => Math.max(max, row.length), 0),
            ...merges.map((merge) => merge.col + merge.colspan - 1),
            1
        );
        const table = document.createElement("table");
        table.className = "ham-sheet-table";

        const colgroup = document.createElement("colgroup");
        const rowHeaderCol = document.createElement("col");
        rowHeaderCol.className = "ham-sheet-row-header-col";
        colgroup.appendChild(rowHeaderCol);
        for (let colIndex = 0; colIndex < colCount; colIndex++) {
            const col = document.createElement("col");
            const width = sheet.col_widths && sheet.col_widths[String(colIndex + 1)];
            if (width) {
                col.style.width = `${Math.max(width * 7, 64)}px`;
            }
            colgroup.appendChild(col);
        }
        table.appendChild(colgroup);

        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        const corner = document.createElement("th");
        corner.className = "ham-sheet-corner";
        headRow.appendChild(corner);
        for (let colIndex = 0; colIndex < colCount; colIndex++) {
            const th = document.createElement("th");
            th.textContent = this._columnName(colIndex + 1);
            headRow.appendChild(th);
        }
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        const coveredMap = this._buildCoveredMap(merges);
        rows.forEach((row, rowIndex) => {
            const tr = document.createElement("tr");
            const rowHeight = sheet.row_heights && sheet.row_heights[String(rowIndex + 1)];
            if (rowHeight) {
                tr.style.height = `${Math.max(rowHeight * 1.33, 24)}px`;
            }
            const th = document.createElement("th");
            th.textContent = String(rowIndex + 1);
            tr.appendChild(th);
            for (let colIndex = 0; colIndex < colCount; colIndex++) {
                if (coveredMap.has(this._cellKey(rowIndex + 1, colIndex + 1))) {
                    continue;
                }
                const td = document.createElement("td");
                td.className = "ham-sheet-cell";
                td.contentEditable = "true";
                td.dataset.rowIndex = String(rowIndex);
                td.dataset.colIndex = String(colIndex);
                const cell = row[colIndex] || { value: "", style: 0 };
                const merge = this._findMerge(merges, rowIndex + 1, colIndex + 1);
                if (merge) {
                    if (merge.colspan > 1) {
                        td.colSpan = merge.colspan;
                    }
                    if (merge.rowspan > 1) {
                        td.rowSpan = merge.rowspan;
                    }
                }
                td.textContent = cell.value || "";
                this._applyCellStyle(td, cell.style);
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        this.gridEl.innerHTML = "";
        this.gridEl.appendChild(table);
    },

    _getCurrentSheet() {
        return this.state.workbook.sheets[this.state.currentSheetIndex];
    },

    _normalizeRows(rows) {
        const normalized = rows && rows.length ? rows.map((row) => row.map((cell) => this._normalizeCell(cell))) : [[this._normalizeCell("")]];
        if (!normalized.length) {
            normalized.push([this._normalizeCell("")]);
        }
        return normalized;
    },

    _onSelectSheet(ev) {
        this.state.currentSheetIndex = Number(ev.currentTarget.dataset.sheetIndex || 0);
        this._render();
    },

    _onCellInput(ev) {
        const cellEl = ev.currentTarget;
        const rowIndex = Number(cellEl.dataset.rowIndex);
        const colIndex = Number(cellEl.dataset.colIndex);
        const sheet = this._getCurrentSheet();
        sheet.rows = this._normalizeRows(sheet.rows);
        while (sheet.rows.length <= rowIndex) {
            sheet.rows.push([]);
        }
        while (sheet.rows[rowIndex].length <= colIndex) {
            sheet.rows[rowIndex].push(this._normalizeCell(""));
        }
        sheet.rows[rowIndex][colIndex].value = cellEl.textContent.replace(/\u00a0/g, " ").trimEnd();
        this.state.dirty = true;
        this._setStatus("Degisiklikler kaydedilmedi.");
    },

    _onAddRow() {
        const sheet = this._getCurrentSheet();
        const rows = this._normalizeRows(sheet.rows);
        const colCount = Math.max(rows.reduce((max, row) => Math.max(max, row.length), 0), 1);
        rows.push(Array.from({ length: colCount }, () => this._normalizeCell("")));
        sheet.rows = rows;
        this.state.dirty = true;
        this._renderGrid();
        this._setStatus("Yeni satir eklendi.");
    },

    _onAddColumn() {
        const sheet = this._getCurrentSheet();
        const rows = this._normalizeRows(sheet.rows);
        rows.forEach((row) => row.push(this._normalizeCell("")));
        sheet.rows = rows;
        this.state.dirty = true;
        this._renderGrid();
        this._setStatus("Yeni sutun eklendi.");
    },

    async _onSave() {
        this._setStatus("Kaydediliyor...");
        const response = await fetch(this.el.dataset.saveUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    workbook: this.state.workbook,
                },
                id: Date.now(),
            }),
        });
        const payload = await response.json();
        const result = payload.result || {};
        if (!result.success) {
            this._setStatus(result.error || "Kayit sirasinda hata olustu.");
            return;
        }
        this.state.dirty = false;
        this._setStatus(result.last_saved_on ? `Kaydedildi: ${result.last_saved_on}` : "Kaydedildi");
    },

    _columnName(index) {
        let value = index;
        let letters = "";
        while (value > 0) {
            const remainder = (value - 1) % 26;
            letters = String.fromCharCode(65 + remainder) + letters;
            value = Math.floor((value - 1) / 26);
        }
        return letters || "A";
    },

    _normalizeCell(cell) {
        if (cell && typeof cell === "object" && !Array.isArray(cell)) {
            return {
                value: cell.value || "",
                style: Number(cell.style || 0),
            };
        }
        return {
            value: cell || "",
            style: 0,
        };
    },

    _applyCellStyle(cellEl, styleIndex) {
        const stylePayload = (this.state.workbook.style_map || [])[styleIndex] || {};
        const css = stylePayload.css || {};
        for (const [key, value] of Object.entries(css)) {
            const normalizedValue = key === "background-color" ? this._normalizeBackgroundColor(value) : value;
            cellEl.style.setProperty(key, normalizedValue);
        }
        const appliedBackground = cellEl.style.getPropertyValue("background-color");
        if (appliedBackground && this._isVeryDarkColor(appliedBackground)) {
            cellEl.style.setProperty("background-color", "#eef2f7");
            if (!cellEl.style.getPropertyValue("color") || this._isVeryDarkColor(cellEl.style.getPropertyValue("color"))) {
                cellEl.style.setProperty("color", "#0f172a");
            }
        }
    },

    _buildCoveredMap(merges) {
        const covered = new Set();
        for (const merge of merges || []) {
            for (let row = merge.row; row < merge.row + merge.rowspan; row++) {
                for (let col = merge.col; col < merge.col + merge.colspan; col++) {
                    if (row === merge.row && col === merge.col) {
                        continue;
                    }
                    covered.add(this._cellKey(row, col));
                }
            }
        }
        return covered;
    },

    _findMerge(merges, row, col) {
        return (merges || []).find((merge) => merge.row === row && merge.col === col);
    },

    _cellKey(row, col) {
        return `${row}:${col}`;
    },

    _normalizeBackgroundColor(value) {
        if (!value || !this._isVeryDarkColor(value)) {
            return value;
        }
        return "#eef2f7";
    },

    _isVeryDarkColor(value) {
        if (!value) {
            return false;
        }
        const hexMatch = value.trim().match(/^#([0-9a-fA-F]{6})$/);
        if (!hexMatch) {
            return false;
        }
        const hex = hexMatch[1];
        const red = parseInt(hex.slice(0, 2), 16);
        const green = parseInt(hex.slice(2, 4), 16);
        const blue = parseInt(hex.slice(4, 6), 16);
        const luminance = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue);
        return luminance < 55;
    },

    _setStatus(message) {
        if (this.statusEl) {
            this.statusEl.textContent = message;
        }
    },
});

export default publicWidget.registry.RonixQualitySpreadsheetEditor;
