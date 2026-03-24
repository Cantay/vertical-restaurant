/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.QrMenuMain = publicWidget.Widget.extend({
    selector: '.qr-menu-container',
    events: {},

    start: function () {
        return this._super.apply(this, arguments);
    },
});
