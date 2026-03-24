/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.FoodSearch = publicWidget.Widget.extend({
    selector: '.js-food-search',
    events: {
        'input': '_onInput',
        'focus': '_onFocus',
    },

    init: function () {
        this._super.apply(this, arguments);
        this._debounceTimer = null;
    },

    start: function () {
        // Find the results container. On home page it might be a level higher due to nested position-relative.
        var $results = this.$el.closest('.position-relative').find('.js-search-results');
        if (!$results.length) {
            $results = this.$el.closest('.position-relative').parent().find('.js-search-results');
        }
        // Final fallback
        if (!$results.length) {
            $results = $('.js-search-results');
        }
        this.$results = $results;
        $(document).on('click.food_search', this._onDocumentClick.bind(this));
        return this._super.apply(this, arguments);
    },

    destroy: function () {
        $(document).off('click.food_search');
        this._super.apply(this, arguments);
    },

    _onInput: function (ev) {
        var self = this;
        var query = $(ev.target).val().trim();

        clearTimeout(this._debounceTimer);
        if (query.length < 2) {
            this._hideResults();
            return;
        }

        this._debounceTimer = setTimeout(function () {
            self._fetchSuggestions(query);
        }, 300);
    },

    _onFocus: function (ev) {
        if ($(ev.target).val().trim().length >= 2) {
            this._showResults();
        }
    },

    _onDocumentClick: function (ev) {
        if (!$(ev.target).closest('.js-food-search, .js-search-results').length) {
            this._hideResults();
        }
    },

    _fetchSuggestions: function (query) {
        var self = this;
        rpc('/food/search_suggestions', { query: query }).then(function (results) {
            self._renderResults(results);
        });
    },

    _renderResults: function (results) {
        var self = this;
        if (!results || results.length === 0) {
            this.$results.html('<div class="p-3 text-muted text-center food-text-sm">Sonuç bulunamadı</div>');
        } else {
            var html = results.map(function (item) {
                var icon = item.type === 'restaurant' ? 'ri-restaurant-2-line' : 'ri-restaurant-line';
                return `
                    <div class="d-flex align-items-center p-3 cursor-pointer food-search-item border-bottom"
                         data-url="${item.url}" data-food-id="${item.food_id || ''}" data-type="${item.type}">
                        <div class="flex-shrink-0 food-w-10 food-h-10 rounded-circle overflow-hidden me-3 border">
                            <img src="${item.image_url}" class="w-100 h-100 object-cover"/>
                        </div>
                        <div class="flex-grow-1 overflow-hidden">
                            <div class="fw-bold text-dark text-truncate food-text-sm">${item.name}</div>
                            <div class="text-secondary food-text-xs">${item.type === 'restaurant' ? 'Restoran' : 'Yemek'}</div>
                        </div>
                        <i class="ri-arrow-right-s-line text-secondary ms-2"></i>
                    </div>
                `;
            }).join('');
            this.$results.html(html);

            // Click handlers for suggestions
            this.$results.find('.food-search-item').on('click', function (ev) {
                var $item = $(ev.currentTarget);
                var url = $item.data('url');
                var foodId = $item.data('food-id');
                var type = $item.data('type');

                if (type === 'food' && foodId) {
                    // If it's a food, we could either go to the restaurant or open the offcanvas
                    // For now, let's go to the restaurant page as defined in the URL
                    window.location.href = url;
                } else {
                    window.location.href = url;
                }
            });
        }
        this._showResults();
    },

    _showResults: function () {
        this.$results.removeClass('d-none').fadeIn(100);
    },

    _hideResults: function () {
        this.$results.addClass('d-none').fadeOut(100);
    },
});
