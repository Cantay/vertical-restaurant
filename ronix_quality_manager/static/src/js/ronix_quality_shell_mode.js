/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityAppShellMode = publicWidget.Widget.extend({
    selector: ".s_ham_shell_mode",

    start() {
        document.body.classList.add("ham-app-shell-mode");
        return this._super(...arguments);
    },

    destroy() {
        if (document.querySelectorAll(".s_ham_shell_mode").length <= 1) {
            document.body.classList.remove("ham-app-shell-mode");
        }
        return this._super(...arguments);
    },
});

export default publicWidget.registry.RonixQualityAppShellMode;
