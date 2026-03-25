/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.QrWaiterCall = publicWidget.Widget.extend({
    selector: '.qr-menu-container',
    events: {
        'click .js-qr-waiter-call-btn': '_onOpenCallModal',
        // NOTE: Modal button events are bound via $(document) in start()
        // because Bootstrap moves modal elements to <body> on .modal('show'),
        // breaking widget event delegation.
    },

    /**
     * Debug logger — only outputs when restaurant.debug_mode is enabled
     * (data-debug="1" on .qr-menu-container)
     */
    _debug: function () {
        if (this._debugEnabled) {
            var args = ['%c[QR-WaiterCall]', 'color: #FF6B35; font-weight: bold;'].concat(
                Array.prototype.slice.call(arguments)
            );
            console.log.apply(console, args);
        }
    },

    /**
     * @override
     */
    start: function () {
        var self = this;
        this._debugEnabled = this.$el.data('debug') === '1' || this.$el.data('debug') === 1;
        this._debug('Widget initialized on', this.el);
        this._debug('Debug mode:', this._debugEnabled ? 'ON' : 'OFF');

        // DOM check
        var $fab = this.$('.js-qr-waiter-call-btn');
        var $modal = $('#waiterCallModal');
        var $successModal = $('#waiterCallSuccessModal');
        var $callBtns = $modal.find('.js-qr-call-type');

        this._debug('DOM elements found:', {
            'FAB button': $fab.length,
            'Call modal': $modal.length,
            'Success modal': $successModal.length,
            'Call type buttons': $callBtns.length,
        });

        if ($fab.length) {
            this._debug('FAB data-restaurant-id:', $fab.data('restaurant-id'));
            this._debug('FAB data-table-id:', $fab.data('table-id'));
        }

        // Bind modal button clicks via document delegation
        // (Bootstrap moves modals to <body>, so widget delegation can't reach them)
        $(document).off('click.qrWaiterCall').on('click.qrWaiterCall', '.js-qr-call-type', function (ev) {
            self._onCallType(ev);
        });
        this._debug('Document-level click handler bound for .js-qr-call-type');

        return this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    destroy: function () {
        $(document).off('click.qrWaiterCall');
        this._super.apply(this, arguments);
    },

    _onOpenCallModal: function (ev) {
        this._debug('FAB clicked — opening call modal');
        var $modal = $('#waiterCallModal');
        this._debug('Modal found in DOM:', $modal.length > 0);

        if ($modal.length) {
            $modal.find('.js-qr-call-type').removeClass('active').prop('disabled', false);
            $modal.find('.js-qr-custom-message').val('');
            $modal.modal('show');
            this._debug('Modal .modal("show") called');
        } else {
            this._debug('ERROR: waiterCallModal not found in DOM!');
        }
    },

    _onCallType: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        var callType = $btn.data('call-type');

        this._debug('Call type button clicked:', callType);

        // Read data from the FAB button (always inside our widget)
        var $fabBtn = this.$('.js-qr-waiter-call-btn');
        var restaurantId = $fabBtn.data('restaurant-id');
        var tableId = $fabBtn.data('table-id');

        // Custom message: modal may have been moved to body, search globally
        var customMessage = $('#waiterCallModal .js-qr-custom-message').val() || '';

        this._debug('RPC params:', {
            restaurant_id: restaurantId,
            table_id: tableId,
            call_type: callType,
            custom_message: customMessage,
        });

        // Validate
        if (!restaurantId || !tableId) {
            this._debug('ERROR: Missing restaurant_id or table_id!');
            this._debug('  FAB found:', $fabBtn.length);
            this._debug('  restaurant_id:', restaurantId, typeof restaurantId);
            this._debug('  table_id:', tableId, typeof tableId);
            alert('Hata: Restoran veya masa bilgisi bulunamadı.');
            return;
        }

        // Visual feedback
        $btn.addClass('active');
        $btn.prop('disabled', true);

        this._debug('Sending RPC to /qr_menu/call_waiter ...');
        var startTime = Date.now();

        rpc('/qr_menu/call_waiter', {
            restaurant_id: restaurantId,
            table_id: tableId,
            call_type: callType,
            custom_message: customMessage,
        }).then(function (result) {
            var duration = Date.now() - startTime;
            self._debug('RPC response (' + duration + 'ms):', result);

            $('#waiterCallModal').modal('hide');

            if (result && result.success) {
                self._debug('Call created successfully, call_id:', result.call_id);
                var $successModal = $('#waiterCallSuccessModal');

                if ($successModal.length) {
                    $successModal.modal('show');
                    setTimeout(function () {
                        $successModal.modal('hide');
                    }, 2500);
                } else {
                    self._debug('WARNING: waiterCallSuccessModal not found');
                }
            } else if (result && result.error) {
                self._debug('Server returned error:', result.error);
                alert(result.error);
            } else {
                self._debug('WARNING: Unexpected response format:', result);
            }

            $btn.removeClass('active').prop('disabled', false);
        }).catch(function (error) {
            var duration = Date.now() - startTime;
            self._debug('RPC FAILED (' + duration + 'ms):', error);
            self._debug('Error name:', error && error.name);
            self._debug('Error message:', error && error.message);
            self._debug('Error data:', error && error.data);

            $btn.removeClass('active').prop('disabled', false);
            alert('Bir hata oluştu. Lütfen tekrar deneyin.');
        });
    },
});
