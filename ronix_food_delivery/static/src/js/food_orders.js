/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.FoodOrders = publicWidget.Widget.extend({
    selector: '.food-app-container',
    events: {
        'click .js-food-open-tip-modal': '_onOpenTipModal',
        'click .js-quick-tip': '_onQuickTipClick',
        'click .js-confirm-standalone-tip': '_onConfirmTip',
    },

    _onOpenTipModal: function (ev) {
        var $btn = $(ev.currentTarget);
        var orderId = $btn.data('order-id');
        var orderName = $btn.data('order-name');

        var $modal = $('#standaloneTipModal');
        $modal.find('.js-tip-target-order-id').val(orderId);
        $modal.find('.js-tip-order-ref').text('Sipariş: ' + orderName);
        $modal.find('.js-standalone-tip-input').val('');
        $modal.find('.js-quick-tip').removeClass('food-bg-orange text-white border-orange').addClass('bg-light text-dark border-light');

        $modal.modal('show');
    },

    _onQuickTipClick: function (ev) {
        var amount = $(ev.currentTarget).data('amount');
        $('.js-standalone-tip-input').val(amount);
        $('.js-quick-tip').removeClass('food-bg-orange text-white border-orange shadow-sm').addClass('bg-light text-dark border-light');
        $(ev.currentTarget).removeClass('bg-light text-dark border-light').addClass('food-bg-orange text-white border-orange shadow-sm');
    },

    _onConfirmTip: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        var orderId = $('.js-tip-target-order-id').val();
        var amount = parseFloat($('.js-standalone-tip-input').val());

        if (isNaN(amount) || amount <= 0) {
            alert('Lütfen geçerli bir bahşiş tutarı giriniz.');
            return;
        }

        $btn.prop('disabled', true).html('<i class="ri-loader-4-line ri-spin"></i> Gönderiliyor...');

        rpc('/food/order/tip/standalone', {
            order_id: parseInt(orderId),
            amount: amount,
        }).then(function (result) {
            if (result.error) {
                self._showStatusModal('error', 'Hata!', result.error);
                $btn.prop('disabled', false).text('Bahşişi Gönder');
            } else {
                $('#standaloneTipModal').modal('hide');
                var $statusModal = self._showStatusModal('success', 'Teşekkürler!', 'Bahşişiniz başarıyla iletildi.');
                $statusModal.one('hidden.bs.modal', function () {
                    window.location.reload();
                });
            }
        });
    },

    _showStatusModal: function (type, title, message) {
        var $modal = $('#foodStatusModal');
        var $iconBg = $modal.find('.js-status-icon-bg');
        var $icon = $modal.find('.js-status-icon');

        $iconBg.removeClass('food-bg-orange-light bg-danger-subtle');
        $icon.removeClass('ri-checkbox-circle-fill ri-error-warning-fill food-text-orange text-danger');

        if (type === 'success') {
            $iconBg.addClass('food-bg-orange-light');
            $icon.addClass('ri-checkbox-circle-fill food-text-orange');
        } else {
            $iconBg.addClass('bg-danger-subtle');
            $icon.addClass('ri-error-warning-fill text-danger');
        }

        $modal.find('.js-status-title').text(title);
        $modal.find('.js-status-message').text(message);

        $modal.modal('show');
        return $modal;
    },
});
