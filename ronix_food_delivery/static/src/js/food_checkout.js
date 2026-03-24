/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.FoodCheckout = publicWidget.Widget.extend({
    selector: '.food-app-container',
    events: {
        'click .js-food-payment-card': '_onCardClick',
        'click .js-food-confirm-payment': '_onConfirmPayment',
    },

    _onCardClick: function (ev) {
        var $card = $(ev.currentTarget);
        var tokenId = $card.data('token-id');

        // Visual update
        $('.js-food-payment-card').removeClass('food-border-orange shadow border-transparent shadow-sm').addClass('border-transparent shadow-sm');
        $card.removeClass('border-transparent shadow-sm').addClass('food-border-orange shadow');

        // Update radio-like indicator
        $('.js-food-payment-card .rounded-circle').removeClass('food-bg-orange food-border-orange border-secondary').addClass('border-secondary');
        $('.js-food-payment-card i.ri-check-line').remove();

        $card.find('.rounded-circle').removeClass('border-secondary').addClass('food-bg-orange food-border-orange');
        $card.find('.rounded-circle').append('<i class="ri-check-line text-white" style="font-size: 0.75rem;"></i>');

        // Enable button
        $('.js-food-confirm-payment').prop('disabled', false).data('token-id', tokenId);
    },

    _onConfirmPayment: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        var tokenId = $btn.data('token-id') || $('.js-food-payment-card.food-border-orange').data('token-id');

        if (!tokenId) {
            alert('Lütfen bir ödeme yöntemi seçin.');
            return;
        }

        $btn.prop('disabled', true).html('<i class="ri-loader-4-line ri-spin"></i> İşleniyor...');

        rpc('/food/checkout/confirm', {
            token_id: tokenId,
        }).then(function (result) {
            if (result.error) {
                alert(result.error);
                $btn.prop('disabled', false).text('Devam Et');
            } else if (result.success) {
                // Success! Redirect to orders or show success page
                window.location.href = '/food-orders?success=1';
            }
        });
    },
});
