/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityInspectionForm = publicWidget.Widget.extend({
    selector: ".ham-inspection-form",
    events: {
        "change .ham-inspection-department-select": "_onDepartmentChange",
        "click .ham-inspection-answer-button": "_onAnswerClick",
    },

    start() {
        this.payloadInputEl = this.el.querySelector(".ham-inspection-line-payload");
        this.departmentSelectEl = this.el.querySelector(".ham-inspection-department-select");
        this.questionListEl = this.el.querySelector(".ham-inspection-question-list-form");
        this.questionMap = JSON.parse(this.questionListEl?.dataset.questionMap || "{}");
        this.el.addEventListener("submit", () => this._syncPayload());
        this._renderQuestions();
        return this._super(...arguments);
    },

    _onDepartmentChange() {
        this._renderQuestions();
    },

    _onAnswerClick(ev) {
        ev.preventDefault();
        const buttonEl = ev.currentTarget;
        const cardEl = buttonEl.closest(".ham-inspection-form-question-card");
        if (!cardEl) {
            return;
        }
        const answer = buttonEl.dataset.answer;
        cardEl.dataset.answer = answer;
        for (const candidate of cardEl.querySelectorAll(".ham-inspection-answer-button")) {
            candidate.classList.toggle("is-active", candidate === buttonEl);
        }
        this._syncPayload();
    },

    _renderQuestions() {
        if (!this.questionListEl || !this.departmentSelectEl) {
            return;
        }
        const departmentId = this.departmentSelectEl.value;
        const questions = this.questionMap[departmentId] || [];
        if (!questions.length) {
            this.questionListEl.innerHTML = `
                <article class="ham-inspection-empty-card ham-inspection-form-empty">
                    <h2>Departman secin</h2>
                    <p>Sorular secilen departmana gore otomatik listelenecek.</p>
                </article>
            `;
            this._syncPayload();
            return;
        }
        this.questionListEl.innerHTML = questions.map((question, index) => `
            <article class="ham-inspection-form-question-card" data-question-id="${question.id}" data-answer="">
                <div class="ham-inspection-form-question-head">
                    <strong>${index + 1}. Soru</strong>
                    <span>${question.weight} Puan</span>
                </div>
                <h3>${this._escapeHtml(question.name)}</h3>
                <div class="ham-inspection-form-answer-row">
                    <button type="button" class="ham-inspection-answer-button" data-answer="yes">Uygun</button>
                    <button type="button" class="ham-inspection-answer-button is-negative" data-answer="no">Uygun Degil</button>
                </div>
            </article>
        `).join("");
        this._syncPayload();
    },

    _syncPayload() {
        if (!this.payloadInputEl || !this.questionListEl) {
            return;
        }
        const rows = [];
        for (const cardEl of this.questionListEl.querySelectorAll(".ham-inspection-form-question-card")) {
            rows.push({
                question_id: cardEl.dataset.questionId,
                answer: cardEl.dataset.answer || "",
            });
        }
        this.payloadInputEl.value = JSON.stringify(rows);
    },

    _escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text || "";
        return div.innerHTML;
    },
});

export default publicWidget.registry.RonixQualityInspectionForm;
