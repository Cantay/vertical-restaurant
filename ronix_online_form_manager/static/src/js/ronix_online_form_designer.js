/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixOnlineFormDesigner = publicWidget.Widget.extend({
    selector: ".s_ronix_online_form_page",
    events: {
        "click .ronix-form-edit-toggle": "_onEnableEdit",
        "click .ronix-form-layout-cancel": "_onCancelEdit",
        "click .ronix-form-layout-save": "_onSaveLayout",
        "click .ronix-field-width-button": "_onWidthClick",
        "dragstart .ronix-form-field-slot": "_onDragStart",
        "dragover .ronix-form-field-slot": "_onDragOver",
        "drop .ronix-form-field-slot": "_onDrop",
        "dragend .ronix-form-field-slot": "_onDragEnd",
    },

    start() {
        this.state = {
            canEdit: this.el.dataset.canEdit === "1",
            isEditing: false,
            draggingFieldId: null,
            isSaving: false,
        };
        this.formEl = this.el.querySelector(".ronix-online-form");
        this.gridEl = this.el.querySelector(".ronix-form-field-grid");
        this.editToggleEl = this.el.querySelector(".ronix-form-edit-toggle");
        this.saveButtonEl = this.el.querySelector(".ronix-form-layout-save");
        this.cancelButtonEl = this.el.querySelector(".ronix-form-layout-cancel");
        this.submitButtonEl = this.el.querySelector(".ronix-form-submit-button");
        return this._super(...arguments);
    },

    _onEnableEdit(ev) {
        ev.preventDefault();
        if (!this.state.canEdit || this.state.isSaving) {
            return;
        }
        this.state.isEditing = true;
        this.el.classList.add("is-layout-editing");
        this._setFormDisabled(true);
        this._toggleButtons();
        this._setFieldsDraggable(true);
        this._syncWidthButtons();
    },

    _onCancelEdit(ev) {
        ev.preventDefault();
        window.location.reload();
    },

    async _onSaveLayout(ev) {
        ev.preventDefault();
        if (!this.state.isEditing || this.state.isSaving) {
            return;
        }
        this.state.isSaving = true;
        this._toggleButtons();
        const response = await fetch(this.el.dataset.saveLayoutUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    layout: this._buildLayoutPayload(),
                },
                id: Date.now(),
            }),
        });
        const payload = await response.json();
        const result = payload.result || {};
        if (!result.success) {
            this.state.isSaving = false;
            this._toggleButtons();
            window.alert(result.error || "Duzen kaydedilemedi.");
            return;
        }
        window.location.reload();
    },

    _onWidthClick(ev) {
        ev.preventDefault();
        if (!this.state.isEditing) {
            return;
        }
        const buttonEl = ev.currentTarget;
        const slotEl = buttonEl.closest(".ronix-form-field-slot");
        if (!slotEl) {
            return;
        }
        const span = buttonEl.dataset.span === "12" ? "12" : "6";
        this._applySpan(slotEl, span);
        this._syncWidthButtons();
    },

    _onDragStart(ev) {
        if (!this.state.isEditing) {
            ev.preventDefault();
            return;
        }
        const slotEl = ev.currentTarget;
        this.state.draggingFieldId = slotEl.dataset.fieldId;
        ev.originalEvent.dataTransfer.effectAllowed = "move";
        ev.originalEvent.dataTransfer.setData("text/plain", this.state.draggingFieldId || "");
        slotEl.classList.add("is-dragging");
    },

    _onDragOver(ev) {
        if (!this.state.isEditing) {
            return;
        }
        ev.preventDefault();
        ev.originalEvent.dataTransfer.dropEffect = "move";
        const targetEl = ev.currentTarget;
        const draggingEl = this._getDraggingElement();
        if (!draggingEl || draggingEl === targetEl || !this.gridEl) {
            return;
        }
        const rect = targetEl.getBoundingClientRect();
        const shouldInsertAfter = ev.originalEvent.clientY > rect.top + rect.height / 2;
        if (shouldInsertAfter) {
            this.gridEl.insertBefore(draggingEl, targetEl.nextSibling);
        } else {
            this.gridEl.insertBefore(draggingEl, targetEl);
        }
    },

    _onDrop(ev) {
        if (!this.state.isEditing) {
            return;
        }
        ev.preventDefault();
    },

    _onDragEnd() {
        this.state.draggingFieldId = null;
        this.el.querySelectorAll(".ronix-form-field-slot.is-dragging").forEach((element) => {
            element.classList.remove("is-dragging");
        });
    },

    _buildLayoutPayload() {
        return Array.from(this.el.querySelectorAll(".ronix-form-field-slot")).map((slotEl) => ({
            field_id: Number(slotEl.dataset.fieldId || 0),
            column_span: slotEl.dataset.fieldType === "section" ? "12" : (slotEl.dataset.columnSpan || "6"),
        }));
    },

    _applySpan(slotEl, span) {
        slotEl.dataset.columnSpan = span;
        slotEl.classList.remove("col-lg-6", "col-lg-12");
        slotEl.classList.add(`col-lg-${span}`);
    },

    _syncWidthButtons() {
        this.el.querySelectorAll(".ronix-form-field-slot").forEach((slotEl) => {
            const span = slotEl.dataset.columnSpan || "6";
            slotEl.querySelectorAll(".ronix-field-width-button").forEach((buttonEl) => {
                buttonEl.classList.toggle("active", buttonEl.dataset.span === span);
            });
        });
    },

    _setFormDisabled(disabled) {
        if (!this.formEl) {
            return;
        }
        this.formEl.querySelectorAll("input, textarea, select").forEach((fieldEl) => {
            if (fieldEl.closest(".ronix-form-field-editor")) {
                return;
            }
            if (fieldEl.type === "hidden") {
                return;
            }
            fieldEl.disabled = disabled;
        });
        if (this.submitButtonEl) {
            this.submitButtonEl.disabled = disabled;
        }
    },

    _setFieldsDraggable(draggable) {
        this.el.querySelectorAll(".ronix-form-field-slot").forEach((slotEl) => {
            slotEl.draggable = draggable;
        });
    },

    _toggleButtons() {
        if (this.editToggleEl) {
            this.editToggleEl.classList.toggle("d-none", this.state.isEditing);
            this.editToggleEl.disabled = this.state.isSaving;
        }
        if (this.saveButtonEl) {
            this.saveButtonEl.classList.toggle("d-none", !this.state.isEditing);
            this.saveButtonEl.disabled = this.state.isSaving;
            this.saveButtonEl.textContent = this.state.isSaving ? "Kaydediliyor..." : "Duzeni Kaydet";
        }
        if (this.cancelButtonEl) {
            this.cancelButtonEl.classList.toggle("d-none", !this.state.isEditing);
            this.cancelButtonEl.disabled = this.state.isSaving;
        }
    },

    _getDraggingElement() {
        if (!this.state.draggingFieldId) {
            return null;
        }
        return this.el.querySelector(`.ronix-form-field-slot[data-field-id="${this.state.draggingFieldId}"]`);
    },
});
