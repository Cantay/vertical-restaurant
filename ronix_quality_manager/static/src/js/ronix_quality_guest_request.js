/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityAppGuestRequestForm = publicWidget.Widget.extend({
    selector: ".s_ham_guest_request",
    events: {
        "submit .ham-request-form": "_onSubmit",
    },

    start() {
        this.statusEl = this.el.querySelector(".ham-request-status");
        this.submitButton = this.el.querySelector(".ham-request-submit");
        this.submitLabel = this.submitButton?.querySelector("span");
        this.defaultSubmitLabel = this.submitLabel?.textContent || "Send Request";
        this.roomFieldEl = this.el.querySelector(".ham-field");
        this.roomInputEl = this.el.querySelector('input[name="room_number"]');
        this._applyRoomNumberFromUrl();
        return this._super(...arguments);
    },

    _applyRoomNumberFromUrl() {
        if (!this.roomInputEl) {
            return;
        }
        const roomNumber = new URLSearchParams(window.location.search).get("room_number");
        if (!roomNumber || !roomNumber.trim()) {
            return;
        }
        this.roomInputEl.value = roomNumber.trim();
        if (this.roomFieldEl) {
            this.roomFieldEl.classList.add("d-none");
        }
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        const form = ev.currentTarget;
        const formData = new FormData(form);
        const requestUrl = (this.el.dataset.requestUrl || "").trim();
        const projectId = (this.el.dataset.projectId || "").trim();

        if (!requestUrl) {
            this._setStatus("is-error", "Request URL is not configured in snippet settings.");
            return;
        }
        if (!projectId) {
            this._setStatus("is-error", "Project ID is not configured in snippet settings.");
            return;
        }
        formData.append("project_id", projectId);

        this._toggleSubmitting(true);
        this._setStatus("", "");

        try {
            const response = await fetch(requestUrl, {
                method: "POST",
                body: formData,
                headers: {
                    Accept: "application/json",
                },
            });
            const contentType = response.headers.get("content-type") || "";
            let result;
            if (contentType.includes("application/json")) {
                result = await response.json();
            } else {
                const responseText = await response.text();
                const compactText = responseText.replace(/\s+/g, " ").trim();
                throw new Error(
                    `The target URL did not return JSON. Check the Request URL. Response starts with: ${compactText.slice(0, 120)}`
                );
            }
            if (!response.ok || !result.success) {
                throw new Error(result.error || "Unable to send the request right now.");
            }

            form.reset();
            this._setStatus(
                "is-success",
                `${result.message} Task: ${result.task_name}`
            );
        } catch (error) {
            this._setStatus("is-error", error.message || "Unable to send the request right now.");
        } finally {
            this._toggleSubmitting(false);
        }
    },

    _toggleSubmitting(isSubmitting) {
        if (this.submitButton) {
            this.submitButton.disabled = isSubmitting;
        }
        if (this.submitLabel) {
            this.submitLabel.textContent = isSubmitting ? "Sending..." : this.defaultSubmitLabel;
        }
    },

    _setStatus(statusClass, message) {
        if (!this.statusEl) {
            return;
        }
        this.statusEl.className = "ham-request-status";
        if (!message) {
            this.statusEl.classList.add("d-none");
            this.statusEl.textContent = "";
            return;
        }
        this.statusEl.classList.remove("d-none");
        if (statusClass) {
            this.statusEl.classList.add(statusClass);
        }
        this.statusEl.textContent = message;
    },
});

export default publicWidget.registry.RonixQualityAppGuestRequestForm;
