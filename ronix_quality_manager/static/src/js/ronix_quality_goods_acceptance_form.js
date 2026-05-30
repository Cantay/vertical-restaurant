/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityGoodsAcceptanceForm = publicWidget.Widget.extend({
    selector: ".ham-goods-acceptance-form",
    events: {
        "click .ham-goods-add-line": "_onAddLine",
        "click .ham-goods-remove-line": "_onRemoveLine",
    },

    start() {
        this.payloadInputEl = this.el.querySelector(".ham-goods-line-payload");
        this.el.addEventListener("submit", () => this._syncPayload());
        this._syncTitles();
        this._syncPayload();
        return publicWidget.Widget.prototype.start.call(this);
    },

    _onAddLine() {
        const lineListEl = this.el.querySelector(".ham-tracking-line-list");
        const firstCard = lineListEl?.querySelector(".ham-tracking-line-card");
        if (!lineListEl || !firstCard) {
            return;
        }
        const clone = firstCard.cloneNode(true);
        for (const input of clone.querySelectorAll("input, select")) {
            if (input.dataset.lineField === "line_date") {
                input.value = this._getToday();
            } else {
                input.value = "";
            }
        }
        lineListEl.appendChild(clone);
        this._syncTitles();
        this._syncPayload();
    },

    _onRemoveLine(ev) {
        const card = ev.currentTarget.closest(".ham-tracking-line-card");
        const lineListEl = card?.closest(".ham-tracking-line-list");
        const cards = lineListEl ? lineListEl.querySelectorAll(".ham-tracking-line-card") : [];
        if (!card || !lineListEl) {
            return;
        }
        if (cards.length === 1) {
            for (const input of card.querySelectorAll("input, select")) {
                if (input.dataset.lineField === "line_date") {
                    input.value = this._getToday();
                } else {
                    input.value = "";
                }
            }
        } else {
            card.remove();
        }
        this._syncTitles();
        this._syncPayload();
    },

    _syncTitles() {
        const cards = this.el.querySelectorAll(".ham-tracking-line-card");
        cards.forEach((card, index) => {
            const titleEl = card.querySelector(".ham-goods-line-title");
            if (titleEl) {
                titleEl.textContent = `${index + 1}. Urun`;
            }
        });
    },

    _isRowEmpty(row) {
        return !Object.values(row).some((value) => value !== false && value !== "");
    },

    _syncPayload() {
        if (!this.payloadInputEl) {
            return;
        }
        const rows = [];
        for (const card of this.el.querySelectorAll(".ham-tracking-line-card")) {
            const row = {};
            for (const input of card.querySelectorAll("[data-line-field]")) {
                row[input.dataset.lineField] = input.value;
            }
            if (!this._isRowEmpty(row)) {
                rows.push(row);
            }
        }
        this.payloadInputEl.value = JSON.stringify(rows);
    },

    _getToday() {
        const today = new Date();
        const year = today.getFullYear();
        const month = `${today.getMonth() + 1}`.padStart(2, "0");
        const day = `${today.getDate()}`.padStart(2, "0");
        return `${year}-${month}-${day}`;
    },
});

export default publicWidget.registry.RonixQualityGoodsAcceptanceForm;
