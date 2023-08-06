import corslite from 'corslite';

import {numberIcon} from '../lib/leaflet-number-marker.js';
import simplestyle from './simplestyle.js';

// loosely based on https://github.com/mapbox/mapbox.js/blob/mb-pages/src/feature_layer.js

function createPopup (properties) {
    if ('no-popup' in properties) {
        return;
    }
    // explicit popup_content takes precedence over other values.
    if ('popup-content' in properties) {
        return properties['popup-content'];
    }

    if ('description' in properties) {
        return properties['description'];
    }
}

function request (url, callback) {
    function onload(err, resp) {
        if (!err && resp) {
            resp = JSON.parse(resp.responseText);
        }
        callback(err, resp);
    }

    return corslite(url, onload);
}

var FeatureLayer = L.FeatureGroup.extend({
    options: {
        filter: function() { return true; },
        style: simplestyle.style,
        popupOptions: { closeButton: false },
        pointToLayer: function (feature, latlng) {
            if ('circle-marker' in feature.properties) {
                var style = simplestyle.style(feature);
                style['radius'] = feature.properties['circle-marker'];

                return L.circleMarker(latlng, style);
            }
            var marker = L.marker(latlng);
            if ('number-marker' in feature.properties) {
                marker.setIcon(numberIcon(feature.properties['number-marker']));
                return marker;
            }

            if ('marker-color' in feature.properties && marker.setIcon) {
                var colorIcon = require('./leaflet-color-icon.js');
                marker.setIcon(colorIcon(feature.properties['marker-color']));
            }
            return marker;
        }
    },
    initialize: function(_, options) {
        L.setOptions(this, options);

        this._layers = {};

        if (typeof _ === 'string') {
            this.loadURL(_);
        } else if (_ && typeof _ === 'object') { // GeoJSON
            this.setGeoJSON(_);
        }
    },

    setGeoJSON: function(_) {
        this._geojson = _;
        this.clearLayers();
        this._initialize(_);
        return this;
    },

    getGeoJSON: function() {
        return this._geojson;
    },

    loadURL: function(url) {
        if (this._request && 'abort' in this._request) this._request.abort();
        this._request = request(url, L.bind(function(err, json) {
            this._request = null;
            if (err && err.type !== 'abort') {
                // eslint-disable-next-line no-console
                console.error('Could not load features at ' + url);
                this.fire('error', {error: err});
            } else if (json) {
                this.setGeoJSON(json);
                this.fire('ready');
            }
        }, this));
        return this;
    },

    setFilter: function(_) {
        this.options.filter = _;
        if (this._geojson) {
            this.clearLayers();
            this._initialize(this._geojson);
        }
        return this;
    },

    getFilter: function() {
        return this.options.filter;
    },

    _initialize: function(json) {
        var features = L.Util.isArray(json) ? json : json.features,
            i, len;

        if (features) {
            for (i = 0, len = features.length; i < len; i++) {
                // Only add this if geometry or geometries are set and not null
                if (features[i].geometries || features[i].geometry || features[i].features) {
                    this._initialize(features[i]);
                }
            }
        } else if (this.options.filter(json)) {
            var layer = L.GeoJSON.geometryToLayer(json, {
                pointToLayer: this.options.pointToLayer
            });

            var style = this.options.style;
            if (style && 'setStyle' in layer) {
                if (typeof style === 'function') {
                    style = style(json);
                }
                layer.setStyle(style);
            }

            layer.feature = json;

            var popupHtml = createPopup(json.properties);
            if (popupHtml) {
                layer.bindPopup(popupHtml, this.options.popupOptions);
            }
            if ('title' in json.properties) {
                layer.bindTooltip(json.properties.title);
            }

            this.addLayer(layer);
        }
    }
});

module.exports.FeatureLayer = FeatureLayer;

module.exports.featureLayer = function(_, options) {
    return new FeatureLayer(_, options);
};
