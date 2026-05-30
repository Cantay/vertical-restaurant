/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityProductTrackingForm = publicWidget.Widget.extend({
    selector: ".ham-tracking-form",
    events: {
        "click .ham-tracking-add-line": "_onAddLine",
        "click .ham-tracking-remove-line": "_onRemoveLine",
        "click .ham-tracking-tag-remove": "_onRemoveTag",
        "change .ham-tracking-tag-picker": "_onTagPickerChange",
        "change select[multiple][data-line-field]": "_onMultiSelectChange",
    },

    start() {
        this.payloadInputEl = this.el.querySelector(".ham-tracking-line-payload");
        this.formEl = this.el;
        this.formEl.addEventListener("submit", () => this._syncPayload());
        this._syncCardTitles();
        this._syncAllTags();
        this._syncPayload();
        return publicWidget.Widget.prototype.start.call(this);
    },

    _onAddLine(ev) {
        const sectionEl = ev.currentTarget.closest(".s_ham_product_tracking_lines");
        const lineListEl = sectionEl?.querySelector(".ham-tracking-line-list");
        const samplePeriod = sectionEl?.dataset.samplePeriod;
        if (!lineListEl || !samplePeriod) {
            return;
        }
        const firstCard = lineListEl.querySelector(".ham-tracking-line-card");
        if (!firstCard) {
            return;
        }
        const clone = firstCard.cloneNode(true);
        for (const input of clone.querySelectorAll("input, select")) {
            if (input.type === "checkbox") {
                input.checked = false;
            } else if (input.type === "date" && firstCard.querySelector(`[data-line-field="${input.dataset.lineField}"]`)?.value) {
                input.value = firstCard.querySelector(`[data-line-field="${input.dataset.lineField}"]`).value;
            } else {
                input.value = "";
            }
            if (input.multiple) {
                for (const option of input.options) {
                    option.selected = false;
                }
            }
        }
        const samplePeriodInput = clone.querySelector('[data-line-field="sample_period"]');
        if (samplePeriodInput) {
            samplePeriodInput.value = samplePeriod;
        }
        lineListEl.appendChild(clone);
        this._syncCardTitles();
        this._syncAllTags();
        this._syncPayload();
    },

    _onRemoveLine(ev) {
        const card = ev.currentTarget.closest(".ham-tracking-line-card");
        if (!card) {
            return;
        }
        const lineListEl = card.closest(".ham-tracking-line-list");
        const cards = lineListEl ? lineListEl.querySelectorAll(".ham-tracking-line-card") : [];
        if (cards.length === 1) {
            for (const input of card.querySelectorAll("input, select")) {
                if (input.type === "checkbox") {
                    input.checked = false;
                } else if (input.dataset.lineField === "sample_period") {
                    continue;
                } else if (input.type !== "date") {
                    input.value = "";
                }
                if (input.multiple) {
                    for (const option of input.options) {
                        option.selected = false;
                    }
                }
            }
        } else {
            card.remove();
        }
        this._syncCardTitles();
        this._syncAllTags();
        this._syncPayload();
    },

    _onMultiSelectChange(ev) {
        this._syncTags(ev.currentTarget);
        this._syncPayload();
    },

    _onTagPickerChange(ev) {
        const picker = ev.currentTarget;
        const field = picker.dataset.tagPickerField;
        const value = picker.value;
        const card = picker.closest(".ham-tracking-line-card");
        const select = card?.querySelector(`select[multiple][data-line-field="${field}"]`);
        if (!select || !value) {
            return;
        }
        const option = [...select.options].find((item) => item.value === value);
        if (option) {
            option.selected = true;
        }
        picker.value = "";
        this._syncTags(select);
        this._syncPayload();
    },

    _onRemoveTag(ev) {
        const button = ev.currentTarget;
        const field = button.dataset.tagField;
        const value = button.dataset.tagValue;
        const card = button.closest(".ham-tracking-line-card");
        const select = card?.querySelector(`select[multiple][data-line-field="${field}"]`);
        if (!select) {
            return;
        }
        const option = [...select.options].find((item) => item.value === value);
        if (option) {
            option.selected = false;
        }
        this._syncTags(select);
        this._syncPayload();
    },

    _syncCardTitles() {
        for (const sectionEl of this.el.querySelectorAll(".s_ham_product_tracking_lines")) {
            const cards = sectionEl.querySelectorAll(".ham-tracking-line-card");
            cards.forEach((card, index) => {
                const titleEl = card.querySelector(".ham-tracking-line-title");
                if (titleEl) {
                    titleEl.textContent = `${index + 1}. Urun`;
                }
            });
        }
    },

    _getRows() {
        const rows = [];
        for (const sectionEl of this.el.querySelectorAll(".s_ham_product_tracking_lines")) {
            const samplePeriod = sectionEl.dataset.samplePeriod;
            for (const card of sectionEl.querySelectorAll(".ham-tracking-line-card")) {
                const row = { sample_period: samplePeriod };
                for (const input of card.querySelectorAll("[data-line-field]")) {
                    row[input.dataset.lineField] = input.multiple ? [...input.selectedOptions].map((option) => option.value) : input.type === "checkbox" ? input.checked : input.value;
                }
                rows.push(row);
            }
        }
        return rows;
    },

    _syncAllTags() {
        for (const select of this.el.querySelectorAll("select[multiple][data-line-field]")) {
            this._syncTags(select);
        }
    },

    _syncTags(select) {
        const field = select.dataset.lineField;
        const card = select.closest(".ham-tracking-line-card");
        const tagBox = card?.querySelector(`[data-tag-field="${field}"]`);
        if (!tagBox) {
            return;
        }
        tagBox.innerHTML = "";
        for (const option of select.selectedOptions) {
            const tag = document.createElement("button");
            tag.type = "button";
            tag.className = "ham-tracking-tag-remove";
            tag.dataset.tagField = field;
            tag.dataset.tagValue = option.value;
            tag.textContent = `${option.textContent} ×`;
            tagBox.appendChild(tag);
        }
    },

    _isRowEmpty(row) {
        return !Object.entries(row).some(([key, value]) => (
            key !== "sample_period" &&
            key !== "line_date" &&
            value !== false &&
            value !== "" &&
            (!Array.isArray(value) || value.length)
        ));
    },

    _syncPayload() {
        if (!this.payloadInputEl) {
            return;
        }
        const rows = this._getRows().filter((row) => !this._isRowEmpty(row));
        this.payloadInputEl.value = JSON.stringify(rows);
    },
});

export default publicWidget.registry.RonixQualityProductTrackingForm;
