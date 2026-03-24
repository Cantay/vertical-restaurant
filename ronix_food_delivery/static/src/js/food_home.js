/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FoodHome = publicWidget.Widget.extend({
    selector: '.food-app-container',
    events: {
        'click .btn-primary': '_onClickFilterPrimary',
    },

    /**
     * @override
     */
    start: function () {
        console.log("Food Home Widget successfully loaded!");
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onClickFilterPrimary: function (ev) {
        // A simple placeholder click handler
        console.log("Filter button clicked!");
    },
});
