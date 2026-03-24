/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.FoodCart = publicWidget.Widget.extend({
    selector: '.food-app-container',
    events: {
        'click .js-food-addon': '_onAddonClick',
        'click .js-addon-qty-plus': '_onAddonQtyPlus',
        'click .js-addon-qty-minus': '_onAddonQtyMinus',
        'click .js-food-qty-plus': '_onQtyPlus',
        'click .js-food-qty-minus': '_onQtyMinus',
        'click .js-food-add-to-cart': '_onAddToCart',
        // Cart Page Events
        'click .js-food-cart-qty-plus': '_onCartQtyPlus',
        'click .js-food-cart-qty-minus': '_onCartQtyMinus',
        'click .js-food-cart-remove': '_onCartRemove',
        'focusout .js-food-order-notes': '_onOrderNotesChange',
        'click .js-food-checkout-btn': '_onCheckout',
        'click .js-confirm-clear-cart': '_onConfirmClearCart',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.selectedAddons = new Map(); // Map of addonId -> quantity
    },

    start: function () {
        this._updateCartUI();
        return this._super.apply(this, arguments);
    },

    // --- Offcanvas Detail Actions ---

    _onAddonClick: function (ev) {
        var $item = $(ev.currentTarget);
        var addonId = parseInt($item.data('addon-id'));
        var type = $item.data('selection-type');

        if (type === 'select') {
            if (this.selectedAddons.has(addonId)) {
                this.selectedAddons.delete(addonId);
                this._toggleAddonUI($item, false);
            } else {
                this.selectedAddons.set(addonId, 1);
                this._toggleAddonUI($item, true);
            }
        } else {
            // For quantity type, if not active, activate it with qty 1
            if (!this.selectedAddons.has(addonId)) {
                this.selectedAddons.set(addonId, 1);
                this._toggleAddonUI($item, true);
                $item.find('.js-addon-qty-value').text(1);
            }
        }
        this._updateOffcanvasPrice();
    },

    _onAddonQtyPlus: function (ev) {
        ev.stopPropagation();
        var $item = $(ev.currentTarget).closest('.js-food-addon');
        var addonId = parseInt($item.data('addon-id'));
        var qty = (this.selectedAddons.get(addonId) || 0) + 1;
        this.selectedAddons.set(addonId, qty);
        $item.find('.js-addon-qty-value').text(qty);
        this._updateOffcanvasPrice();
    },

    _onAddonQtyMinus: function (ev) {
        ev.stopPropagation();
        var $item = $(ev.currentTarget).closest('.js-food-addon');
        var addonId = parseInt($item.data('addon-id'));
        var qty = (this.selectedAddons.get(addonId) || 0) - 1;

        if (qty <= 0) {
            this.selectedAddons.delete(addonId);
            this._toggleAddonUI($item, false);
        } else {
            this.selectedAddons.set(addonId, qty);
            $item.find('.js-addon-qty-value').text(qty);
        }
        this._updateOffcanvasPrice();
    },

    _toggleAddonUI: function ($item, active) {
        var type = $item.data('selection-type');
        if (active) {
            $item.addClass('active food-border-orange bg-orange-light');
            $item.find('.selection-indicator i').removeClass('ri-checkbox-blank-circle-line text-secondary').addClass('ri-checkbox-circle-fill text-orange');
            if (type === 'quantity') {
                $item.find('.js-addon-qty-container').removeClass('d-none');
                $item.find('.js-addon-qty-trigger').hide();
            }
        } else {
            $item.removeClass('active food-border-orange bg-orange-light');
            $item.find('.selection-indicator i').removeClass('ri-checkbox-circle-fill text-orange').addClass('ri-checkbox-blank-circle-line text-secondary');
            if (type === 'quantity') {
                $item.find('.js-addon-qty-container').addClass('d-none');
                $item.find('.js-addon-qty-trigger').show();
            }
        }
    },

    _onQtyPlus: function () {
        var $val = this.$('.js-food-qty-value');
        $val.text(parseInt($val.text()) + 1);
        this._updateOffcanvasPrice();
    },

    _onQtyMinus: function () {
        var $val = this.$('.js-food-qty-value');
        var qty = parseInt($val.text());
        if (qty > 1) {
            $val.text(qty - 1);
        }
        this._updateOffcanvasPrice();
    },

    _updateOffcanvasPrice: function () {
        var basePrice = parseFloat(this.$('.js-food-add-to-cart').data('base-price')) || 0;
        var qty = parseInt(this.$('.js-food-qty-value').text()) || 1;
        var addonPrice = 0;

        this.selectedAddons.forEach((addonQty, id) => {
            var price = parseFloat($(`.js-food-addon[data-addon-id="${id}"]`).data('extra-price')) || 0;
            addonPrice += (price * addonQty);
        });

        var total = (basePrice + addonPrice) * qty;
        this.$('.js-food-total-price').text('$' + (total || 0).toFixed(2));
    },

    _onAddToCart: function (ev) {
        var self = this;
        var $btn = $(ev.currentTarget);
        var productId = $btn.data('food-id');
        var qty = parseInt(this.$('.js-food-qty-value').text()) || 1;

        var addons = [];
        this.selectedAddons.forEach((addonQty, id) => {
            addons.push({ id: id, qty: addonQty });
        });

        $btn.prop('disabled', true).addClass('opacity-50');

        rpc('/food/cart/add_json', {
            product_id: productId,
            quantity: qty,
            addons: addons,
        }).then(function (result) {
            $btn.prop('disabled', false).removeClass('opacity-50');
            if (result.error === 'different_restaurant') {
                self.pendingProduct = {
                    product_id: productId,
                    quantity: qty,
                    addons: addons
                };
                var $modal = $('#differentRestaurantModal');
                $modal.find('.js-current-res-name').text(result.current_restaurant);
                $modal.find('.js-new-res-name').text(result.new_restaurant);
                $modal.modal('show');
            } else if (result.error === 'address_required') {
                $('#addressRequiredModal').modal('show');
            } else if (result.error) {
                alert(result.error);
            } else {
                // Close offcanvas
                $('.offcanvas').offcanvas('hide');
                self._updateCartSummary(result);
                // Reset selection for next open
                self.selectedAddons.clear();
                self.$('.js-food-qty-value').text(1);
            }
        });
    },

    _onConfirmClearCart: function () {
        var self = this;
        if (!this.pendingProduct) return;

        rpc('/food/cart/clear_and_add', this.pendingProduct).then(function (result) {
            $('#differentRestaurantModal').modal('hide');
            self.pendingProduct = null;
            if (!result.error) {
                window.location.href = '/food-cart'; // Redirect to cart to show fresh state
            }
        });
    },

    _onCheckout: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var self = this;
        rpc('/food/cart/get_summary', {}).then(function (result) {
            var minAmount = parseFloat(result.min_order_amount || 0);
            var untaxed = parseFloat(result.cart_untaxed || 0);

            if (untaxed < minAmount) {
                var needed = minAmount - untaxed;
                var $modal = $('#minOrderModal');
                $modal.find('.js-popup-min-amount').text('$' + minAmount.toFixed(2));
                $modal.find('.js-popup-needed-amount').text('$' + needed.toFixed(2));
                var restaurantUrl = result.restaurant_url || '/food';
                $modal.find('.js-goto-restaurant').attr('href', restaurantUrl);
                $modal.modal('show');
            } else {
                window.location.href = '/food/checkout/payment';
            }
        });
    },

    // --- Cart Page Actions ---

    _onCartQtyPlus: function (ev) {
        var $line = $(ev.currentTarget).closest('.js-food-cart-item');
        var lineId = $line.data('line-id');
        var $val = $line.find('.js-food-cart-qty-value');
        var newQty = parseInt($val.text()) + 1;
        this._updateLineQuantity(lineId, newQty, $line);
    },

    _onCartQtyMinus: function (ev) {
        var $line = $(ev.currentTarget).closest('.js-food-cart-item');
        var lineId = $line.data('line-id');
        var $val = $line.find('.js-food-cart-qty-value');
        var newQty = parseInt($val.text()) - 1;
        this._updateLineQuantity(lineId, newQty, $line);
    },

    _onCartRemove: function (ev) {
        var self = this;
        var $line = $(ev.currentTarget).closest('.js-food-cart-item');
        var lineId = $line.data('line-id');

        rpc('/food/cart/remove_item', { line_id: lineId }).then(function (result) {
            $line.fadeOut(300, function () {
                $(this).remove();
                self._updateCartSummary(result);
                if ($('.js-food-cart-item').length === 0) {
                    location.reload(); // Show empty state
                }
            });
        });
    },

    _updateLineQuantity: function (lineId, quantity, $line) {
        var self = this;
        rpc('/food/cart/update_quantity', { line_id: lineId, quantity: quantity }).then(function (result) {
            if (quantity <= 0) {
                $line.remove();
                if ($('.js-food-cart-item').length === 0) location.reload();
            } else {
                $line.find('.js-food-cart-qty-value').text(quantity);
                $line.find('.food-text-orange').text('$' + parseFloat(result.line_price_total || 0).toFixed(2));
            }
            self._updateCartSummary(result);
        });
    },

    _updateCartSummary: function (data) {
        // Update counts in header and nav
        $('.js-food-cart-count-summary').text(data.cart_quantity + ' ürün');
        $('.js-cart-badge').text(data.cart_quantity).toggle(data.cart_quantity > 0);

        // Update totals in cart page
        $('.js-food-untaxed-amount').text('$' + parseFloat(data.cart_untaxed || 0).toFixed(2));
        $('.js-food-tax-amount').text('$' + parseFloat(data.cart_tax || 0).toFixed(2));

        var deliveryFee = parseFloat(data.cart_delivery_fee || 0);
        $('.js-food-delivery-fee').text(deliveryFee > 0 ? '$' + deliveryFee.toFixed(2) : 'Ücretsiz');

        $('.js-food-total-amount').text('$' + parseFloat(data.cart_total || 0).toFixed(2));

        // Min Order Amount Check
        var untaxed = parseFloat(data.cart_untaxed || 0);
        var minAmount = parseFloat(data.min_order_amount || 0);
        var $warning = $('.js-food-min-order-warning');
        var $checkoutBtn = $('.fixed-bottom button:contains("Sipariş Ver"), .fixed-bottom button:contains("Order Now")');

        if (untaxed < minAmount) {
            $warning.removeClass('d-none');
            $warning.find('.js-food-min-amount-val').text(minAmount.toFixed(2));
        } else {
            $warning.addClass('d-none');
        }

        $('.js-food-checkout-total').text(parseFloat(data.cart_total || 0).toFixed(2));
    },

    _onOrderNotesChange: function (ev) {
        var notes = $(ev.currentTarget).val();
        rpc('/food/cart/update_notes', { notes: notes });
    },

    _updateCartUI: function () {
        // Fetch current state on load
        rpc('/food/cart/get_summary', {}).then(function (result) {
            $('.js-cart-badge').text(result.cart_quantity).toggle(result.cart_quantity > 0);
        });
    }
});
