/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.QrWaiterCall = publicWidget.Widget.extend({
    selector: '.qr-menu-container',
    events: {
        'click .js-qr-waiter-call-btn': '_onOpenCallModal',
        'click .js-qr-call-type': '_onCallType',
    },

    _onOpenCallModal: function (ev) {
        var $modal = $('#waiterCallModal');
        if ($modal.length) {
            // Reset state
            $modal.find('.js-qr-call-type').removeClass('active');
            $modal.find('.js-qr-custom-message').val('');
            // Bootstrap 5 modal
            var modal = bootstrap.Modal.getOrCreateInstance($modal[0]);
            modal.show();
        }
    },

    _onCallType: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        var callType = $btn.data('call-type');
        var $fabBtn = this.$('.js-qr-waiter-call-btn');
        var restaurantId = $fabBtn.data('restaurant-id');
        var tableId = $fabBtn.data('table-id');
        var customMessage = this.$('.js-qr-custom-message').val() || '';

        // Visual feedback
        $btn.addClass('active');
        $btn.prop('disabled', true);

        rpc('/qr_menu/call_waiter', {
            restaurant_id: restaurantId,
            table_id: tableId,
            call_type: callType,
            custom_message: customMessage,
        }).then(function (result) {
            // Close call modal
            var callModal = bootstrap.Modal.getInstance($('#waiterCallModal')[0]);
            if (callModal) callModal.hide();

            if (result.success) {
                // Show success modal
                var $successModal = $('#waiterCallSuccessModal');
                if ($successModal.length) {
                    var successModal = bootstrap.Modal.getOrCreateInstance($successModal[0]);
                    successModal.show();
                    setTimeout(function () {
                        successModal.hide();
                    }, 2500);
                }
            } else if (result.error) {
                alert(result.error);
            }

            $btn.removeClass('active').prop('disabled', false);
        }).catch(function () {
            $btn.removeClass('active').prop('disabled', false);
            alert('Bir hata oluştu. Lütfen tekrar deneyin.');
        });
    },
});
