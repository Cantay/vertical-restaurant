/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.QrArViewer = publicWidget.Widget.extend({
    selector: '.qr-menu-container',
    events: {
        'click .js-qr-ar-load': '_onLoadAr',
    },

    _modelViewerLoaded: false,

    _onLoadAr: function (ev) {
        var self = this;
        var $container = $(ev.currentTarget).closest('.js-qr-ar-container');
        var modelUrl = $container.data('model-url');

        if (!modelUrl) return;

        // Show loading
        $container.find('.js-qr-ar-placeholder').html(
            '<div class="spinner-border text-primary" role="status"></div>'
        );

        // Lazy load model-viewer if not yet loaded
        if (!this._modelViewerLoaded && !document.querySelector('script[src*="model-viewer"]')) {
            var script = document.createElement('script');
            script.type = 'module';
            script.src = 'https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js';
            script.onload = function () {
                self._modelViewerLoaded = true;
                self._renderModelViewer($container, modelUrl);
            };
            document.head.appendChild(script);
        } else {
            this._renderModelViewer($container, modelUrl);
        }
    },

    _renderModelViewer: function ($container, modelUrl) {
        var html = '<model-viewer ' +
            'src="' + modelUrl + '" ' +
            'alt="3D Model" ' +
            'auto-rotate ' +
            'camera-controls ' +
            'touch-action="pan-y" ' +
            'ar ' +
            'ar-modes="webxr scene-viewer quick-look" ' +
            'style="width: 100%; height: 300px; background: #f8f9fa;" ' +
            'loading="eager">' +
            '<div class="progress-bar" slot="progress-bar"></div>' +
            '</model-viewer>';

        $container.html(html);
    },
});
