/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.RonixQualityAppVipHeader = publicWidget.Widget.extend({
    selector: ".s_app_vip_header",
    events: {
        "click .ham-vip-menu-toggle": "_onOpenMenu",
        "click .ham-vip-menu-close": "_onCloseMenu",
        "click .ham-vip-menu-backdrop": "_onCloseMenu",
        "click .ham-vip-side-link": "_onCloseMenu",
    },

    start() {
        this._setMenuOpen(false);
        return this._super(...arguments);
    },

    _onOpenMenu(ev) {
        ev.preventDefault();
        this._setMenuOpen(true);
    },

    _onCloseMenu(ev) {
        ev.preventDefault();
        this._setMenuOpen(false);
    },

    _setMenuOpen(isOpen) {
        this.el.classList.toggle("is-menu-open", isOpen);
        const menuToggle = this.el.querySelector(".ham-vip-menu-toggle");
        const sideMenu = this.el.querySelector(".ham-vip-side-menu");
        if (menuToggle) {
            menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        }
        if (sideMenu) {
            sideMenu.setAttribute("aria-hidden", isOpen ? "false" : "true");
        }
    },
});

export default publicWidget.registry.RonixQualityAppVipHeader;
