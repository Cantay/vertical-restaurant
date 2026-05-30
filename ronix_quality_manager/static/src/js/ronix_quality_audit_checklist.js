/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

const CONFETTI_COLORS = ["#f4d799", "#fff0cf", "#e3bf73", "#ffffff", "#d69d43"];

publicWidget.registry.RonixQualityAuditChecklist = publicWidget.Widget.extend({
    selector: ".s_ham_audit_page",
    events: {
        "click .ham-audit-group-toggle": "_onToggleGroup",
        "change .ham-audit-checkbox": "_onToggleItem",
    },

    start() {
        this._initializeAllGroups();
        return this._super(...arguments);
    },

    _initializeAllGroups() {
        for (const groupEl of this.el.querySelectorAll(".ham-audit-group")) {
            this._initializeGroup(groupEl);
        }
    },

    _initializeGroup(groupEl) {
        groupEl.classList.remove("is-open");
        groupEl.dataset.isDone = "0";
        for (const itemEl of groupEl.querySelectorAll(".ham-audit-item")) {
            const checkbox = itemEl.querySelector(".ham-audit-checkbox");
            if (!checkbox) {
                continue;
            }
            checkbox.checked = false;
            itemEl.classList.remove("is-checked");
        }

        this._updateGroupProgress(groupEl, { animate: false });
    },

    _onToggleGroup(ev) {
        ev.preventDefault();
        const groupEl = ev.currentTarget.closest(".ham-audit-group");
        if (!groupEl) {
            return;
        }
        const isOpen = !groupEl.classList.contains("is-open");
        groupEl.classList.toggle("is-open", isOpen);
    },

    _onToggleItem(ev) {
        const checkbox = ev.currentTarget;
        const itemEl = checkbox.closest(".ham-audit-item");
        const groupEl = checkbox.closest(".ham-audit-group");
        if (!itemEl || !groupEl) {
            return;
        }

        const isChecked = checkbox.checked;
        itemEl.classList.toggle("is-checked", isChecked);
        this._updateGroupProgress(groupEl, { animate: true });
    },

    _updateGroupProgress(groupEl, { animate = false } = {}) {
        const items = [...groupEl.querySelectorAll(".ham-audit-item")];
        const total = items.length;
        const checked = items.filter((itemEl) => itemEl.classList.contains("is-checked")).length;
        const statusEl = groupEl.querySelector(".ham-audit-status");
        const countEl = groupEl.querySelector(".ham-audit-count");
        const wasDone = groupEl.dataset.isDone === "1";
        const isDone = total > 0 && checked === total;

        if (countEl) {
            countEl.textContent = `${checked}/${total}`;
        }
        if (statusEl) {
            statusEl.classList.toggle("is-visible", isDone);
        }
        groupEl.dataset.isDone = isDone ? "1" : "0";
        if (animate && isDone && !wasDone) {
            this._triggerCelebration(groupEl);
        }
    },

    _triggerCelebration(groupEl) {
        const existingLayer = groupEl.querySelector(".ham-audit-confetti-layer");
        if (existingLayer) {
            existingLayer.remove();
        }

        const layer = document.createElement("div");
        layer.className = "ham-audit-confetti-layer";

        for (let index = 0; index < 42; index++) {
            const piece = document.createElement("span");
            piece.className = "ham-audit-confetti-piece";
            piece.style.setProperty("--confetti-left", `${8 + Math.random() * 84}%`);
            piece.style.setProperty("--confetti-delay", `${Math.random() * 0.45}s`);
            piece.style.setProperty("--confetti-duration", `${2.8 + Math.random() * 1.4}s`);
            piece.style.setProperty("--confetti-drift", `${-80 + Math.random() * 160}px`);
            piece.style.setProperty("--confetti-rotate", `${180 + Math.random() * 540}deg`);
            piece.style.setProperty("--confetti-size", `${8 + Math.random() * 10}px`);
            piece.style.setProperty(
                "--confetti-color",
                CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)]
            );
            layer.appendChild(piece);
        }

        groupEl.appendChild(layer);
        window.setTimeout(() => layer.remove(), 4200);
    },
});

export default publicWidget.registry.RonixQualityAuditChecklist;
