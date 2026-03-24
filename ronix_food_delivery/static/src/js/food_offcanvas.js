/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.FoodOffcanvas = publicWidget.Widget.extend({
    selector: '.js-open-food-detail',
    events: {
        'click': '_onClickFoodDetail',
    },

    _onClickFoodDetail: function (ev) {
        var $card = $(ev.currentTarget);
        var foodId = $card.data('food-id');
        var $offcanvasElement = $('#foodDetailOffcanvas');

        // Show loading placeholder initially to give instant feedback
        var loadingHtml = '<div class="d-flex justify-content-center align-items-center" style="height: 300px;"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
        $offcanvasElement.html(loadingHtml);

        // Fetch the dynamic content snippet from the server
        rpc('/food/offcanvas/' + foodId, {}).then(function (htmlStr) {
            // Replace loading with real HTML
            $offcanvasElement.html(htmlStr);
        }).catch(function (error) {
            console.error("Failed to fetch food details:", error);
            $offcanvasElement.html('<div class="p-4 text-center text-danger">Yemek detayları yüklenemedi. Lütfen tekrar deneyin.</div>');
        });
    },
});
