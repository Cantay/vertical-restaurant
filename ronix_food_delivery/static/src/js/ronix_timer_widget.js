/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onWillDestroy, onMounted, useState, xml } from "@odoo/owl";

export class RonixTimerWidget extends Component {
    static template = xml`
        <span t-esc="state.displayValue" class="badge rounded-pill fw-bold px-2 py-1" style="font-size: 0.75rem; min-width: 70px; display: inline-block; color: white !important; background-color: #dc3545 !important;"/>
    `;
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            displayValue: "",
        });
        onMounted(() => {
            this._updateTimer();
            this.timer = setInterval(() => this._updateTimer(), 1000);
        });
        onWillDestroy(() => {
            clearInterval(this.timer);
        });
    }

    _updateTimer() {
        const val = this.props.record.data[this.props.name];
        if (!val) {
            this.state.displayValue = "-";
            return;
        }

        try {
            let start;
            if (typeof val === 'string') {
                start = luxon.DateTime.fromSQL(val, { zone: 'utc' });
            } else if (luxon.DateTime.isDateTime(val)) {
                start = val.toUTC();
            } else {
                this.state.displayValue = "-";
                return;
            }

            const now = luxon.DateTime.utc();
            const diff = now.diff(start, ["minutes", "seconds"]).toObject();

            const mins = Math.max(0, Math.floor(diff.minutes || 0));
            const secs = Math.max(0, Math.floor(diff.seconds || 0));

            this.state.displayValue = `${mins} dk ${secs} sn`;
        } catch (e) {
            console.error("Ronix Timer Error:", e);
            this.state.displayValue = "err";
        }
    }
}

export const ronixTimerField = {
    component: RonixTimerWidget,
    supportedTypes: ["datetime"],
};

registry.category("fields").add("ronix_timer", ronixTimerField);
