/** @odoo-module **/

import { useEffect, useRef } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";

const TARGET_MODEL = "ronix.quality.operational.nonconformity";
const TARGET_FIELDS = new Set(["nonconformity_date", "deadline_date"]);

patch(DateTimeField.prototype, {
    setup() {
        super.setup(...arguments);

        const startDateRef = useRef("start-date");
        const endDateRef = useRef("end-date");

        useEffect(
            () => {
                if (this.props.record?.resModel !== TARGET_MODEL || !TARGET_FIELDS.has(this.props.name)) {
                    return;
                }
                for (const input of [startDateRef.el, endDateRef.el]) {
                    if (!input) {
                        continue;
                    }
                    input.inputMode = "none";
                    input.readOnly = true;
                    input.setAttribute("readonly", "readonly");
                }
            },
            () => [this.props.record?.resModel, this.props.name, startDateRef.el, endDateRef.el]
        );
    },
});
