/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AddressManagement = publicWidget.Widget.extend({
    selector: '.food-app-container',
    events: {
        'click .edit-address-btn': '_onEditAddressClick',
        'click .add-new-address-btn': '_onAddNewAddressClick',
        'submit #newAddressOffcanvas form': '_onAddressSubmit',
    },

    start: function () {
        this._initGoogleAutocomplete();
        return this._super.apply(this, arguments);
    },

    _initGoogleAutocomplete: function () {
        var self = this;
        var apiKey = this.$el.data('google-maps-api-key');
        if (!apiKey) return;

        if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
            var script = document.createElement('script');
            script.src = 'https://maps.googleapis.com/maps/api/js?key=' + apiKey + '&libraries=places&language=tr';
            script.async = true;
            script.defer = true;
            script.onload = function () {
                self._setupAutocomplete();
            };
            document.head.appendChild(script);
        } else {
            this._setupAutocomplete();
        }
    },

    _setupAutocomplete: function () {
        var input = document.querySelector('textarea[name="address_details"]');
        if (input) {
            var autocomplete = new google.maps.places.Autocomplete(input);
            autocomplete.addListener('place_changed', function () {
                var place = autocomplete.getPlace();
                if (!place.geometry) return;

                var lat = place.geometry.location.lat();
                var lng = place.geometry.location.lng();

                var $offcanvas = $('#newAddressOffcanvas');
                $offcanvas.find('input[name="lat"]').val(lat);
                $offcanvas.find('input[name="lng"]').val(lng);
            });
        }
    },

    _onEditAddressClick: function (ev) {
        var $btn = $(ev.currentTarget);
        var addressId = $btn.data('address-id');
        var addressTitle = $btn.data('address-name');
        var addressCity = $btn.data('address-city');
        var addressDistrict = $btn.data('address-district');
        var addressDetails = $btn.data('address-details');
        var addressDirections = $btn.data('address-directions');
        var addressLat = $btn.data('address-lat') || '';
        var addressLng = $btn.data('address-lng') || '';

        var $offcanvas = $('#newAddressOffcanvas');
        $offcanvas.find('#newAddressOffcanvasLabel').text('Adresi Düzenle');
        $offcanvas.find('form').attr('action', '/food/address/edit');

        // Add or update hidden address_id input
        var $idInput = $offcanvas.find('input[name="address_id"]');
        if ($idInput.length === 0) {
            $offcanvas.find('form').append('<input type="hidden" name="address_id" value="' + addressId + '"/>');
        } else {
            $idInput.val(addressId);
        }

        $offcanvas.find('input[name="address_title"]').val(addressTitle);
        $offcanvas.find('input[name="city"]').val(addressCity);
        $offcanvas.find('input[name="district"]').val(addressDistrict);
        $offcanvas.find('textarea[name="address_details"]').val(addressDetails);
        $offcanvas.find('input[name="address_directions"]').val(addressDirections);
        $offcanvas.find('input[name="lat"]').val(addressLat);
        $offcanvas.find('input[name="lng"]').val(addressLng);

        // Change button text
        $offcanvas.find('button[type="submit"]').text('Adresi Güncelle');
    },

    _onAddNewAddressClick: function (ev) {
        var $offcanvas = $('#newAddressOffcanvas');
        $offcanvas.find('#newAddressOffcanvasLabel').text('Yeni Adres Ekle');
        $offcanvas.find('form').attr('action', '/food/address/add');
        $offcanvas.find('input[name="address_id"]').remove();

        $offcanvas.find('input[name="address_title"]').val('');
        $offcanvas.find('input[name="city"]').val('');
        $offcanvas.find('input[name="district"]').val('');
        $offcanvas.find('textarea[name="address_details"]').val('');
        $offcanvas.find('input[name="address_directions"]').val('');
        $offcanvas.find('input[name="lat"]').val('');
        $offcanvas.find('input[name="lng"]').val('');

        $offcanvas.find('button[type="submit"]').text('Adresi Kaydet');
    },

    _onAddressSubmit: function (ev) {
        var $form = $(ev.currentTarget);
        var lat = $form.find('input[name="lat"]').val();
        var lng = $form.find('input[name="lng"]').val();

        if (!lat || lat === '0' || lat === '0.0' || lat === '0.000000' ||
            !lng || lng === '0' || lng === '0.0' || lng === '0.000000') {

            ev.preventDefault();

            var city = $form.find('input[name="city"]').val() || '';
            var district = $form.find('input[name="district"]').val() || '';
            var details = $form.find('textarea[name="address_details"]').val() || '';
            var fullAddress = [details, district, city, "Türkiye"].filter(Boolean).join(", ");

            if (typeof google !== 'undefined' && google.maps && google.maps.Geocoder) {
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode({ 'address': fullAddress }, function (results, status) {
                    if (status === 'OK' && results[0]) {
                        var location = results[0].geometry.location;
                        $form.find('input[name="lat"]').val(location.lat());
                        $form.find('input[name="lng"]').val(location.lng());
                    }
                    $form[0].submit();
                });
            } else {
                $form[0].submit();
            }
        }
    }
});
