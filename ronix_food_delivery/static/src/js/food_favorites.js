/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

// Widget for static favorite buttons (Restaurants on lists/home)
publicWidget.registry.FoodFavorites = publicWidget.Widget.extend({
    selector: '.js-food-toggle-favorite',
    events: {
        'click': '_onClickFavorite',
    },

    _onClickFavorite: function (ev) {
        ev.preventDefault();
        ev.stopPropagation(); // Stops bubbling to the restaurant card redirect

        var $btn = $(ev.currentTarget);
        var restaurantId = $btn.data('restaurant-id');
        var $icon = $btn.find('i');

        rpc('/food/toggle_favorite', {
            restaurant_id: restaurantId,
        }).then(function (data) {
            if (data.error) return;
            if (data.is_favorite) {
                $icon.removeClass('ri-heart-line text-secondary text-muted').addClass('ri-heart-fill text-danger');
            } else {
                $icon.removeClass('ri-heart-fill text-danger').addClass('ri-heart-line text-secondary');
            }
        });
    },
});

// Widget for dynamic favorite buttons (Food details inside Offcanvas)
publicWidget.registry.FoodFavoritesDynamic = publicWidget.Widget.extend({
    selector: '#foodDetailOffcanvas', // This shell exists on page load
    events: {
        'click .js-food-toggle-favorite-food': '_onClickFavoriteFood',
    },

    _onClickFavoriteFood: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var $btn = $(ev.currentTarget);
        var foodId = $btn.data('food-id');
        var $icon = $btn.find('i');

        rpc('/food/toggle_favorite_food', {
            food_id: foodId,
        }).then(function (data) {
            if (data.error) return;
            if (data.is_favorite) {
                $icon.removeClass('ri-heart-line text-secondary text-muted').addClass('ri-heart-fill text-danger');
            } else {
                $icon.removeClass('ri-heart-fill text-danger').addClass('ri-heart-line text-secondary');
            }
        });
    },
});
