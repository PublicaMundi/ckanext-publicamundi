/* 
 * Module for handling the spatial editing 
 * This is modified version of the spatial-query module.
 */
this.ckan.module('publicamundi-spatial-edit', function ($, _) {

  return {
    options: {
      i18n: {},
      style: {
        color: '#F06F64',
        weight: 2,
        opacity: 1,
        fillColor: '#F06F64',
        fillOpacity: 0.1
      },
      input: '#field-geographic_coverage',
      extent: null,
      bbox: { 
        type: 'Polygon', 
        coordinates: [[[19.190674,34.800395],[30.264893,34.800395],[30.264893,41.82466],[19.190674,41.82466],[19.190674,34.800395]]]
      },
    },

    initialize: function () {
      var module = this;

      $.proxyAll(this, /^_on/);

      // Assume extent and bbox are valid GeoJSON objects (or null)
              
      if (!(this.options.extent instanceof Object)) {
         this.options.extent = null
      }
      if (this.options.extent) {
        this.options.extent = new L.GeoJSON(this.options.extent, { style: this.options.style })
      }
       
      if (!(this.options.bbox instanceof Object)) {
         this.options.bbox = null
      }
      if (this.options.bbox) {
        this.options.bbox   = new L.GeoJSON(this.options.bbox)
      } 
      
      // If the widget is embeded inside a dialog/accordion, initialize it when it shows up,
      // otherwise initialize it when document is loaded.

      if (this.el.is('.modal') || this.el.is('.collapse')) {
        this.el.on('shown', this._onReady);
      } else {
        this.el.ready(this._onReady);
      }
      
      return 
    },

    _onReady: function() {
      var module = this;
      var map1;
      var extent_layer, bbox;

      try {
        map1 = new L.Map('dataset-map-container', {attributionControl: false});
      } catch (ex) {
        console.info('Cannot (re)initialize leaflet map container')
        return;
      } 

      // MapQuest OpenStreetMap base map
      map1.addLayer(new L.TileLayer(
        'http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
         {maxZoom: 18, subdomains: '1234'}
      ));

      // Initialize the draw control
      map1.addControl(new L.Control.Draw({
        position: 'topright',
        polyline: false, 
        polygon: {
          shapeOptions: module.options.style,
          title: 'Draw a polygon'
        },
        circle: false, 
        marker: false,
        rectangle: {
          shapeOptions: module.options.style,
          title: 'Draw a rectangle'
        }
      }));
 
      extent_layer = this.options.extent
      bbox         = this.options.bbox;

      if (extent_layer) {
        map1.addLayer(extent_layer);
        map1.fitBounds(extent_layer.getBounds());
      } else if (bbox) {
        map1.fitBounds(bbox.getBounds());
      }

      // When user finishes drawing the box, record it and add it to the map
      
      map1.on('draw:rectangle-created', function (e) {
        if (extent_layer) {
          map1.removeLayer(extent_layer);
        }
        extent_layer = e.rect;
        map1.addLayer(extent_layer);
      });
      
      map1.on('draw:poly-created', function (e) {
        if (extent_layer) {
          map1.removeLayer(extent_layer);
        }
        extent_layer = e.poly;
        map1.addLayer(extent_layer);
      });
       
      map1.on('draw:poly-created', this._onPolyCreated);
      
      map1.on('draw:rectangle-created', this._onRectCreated);

      this.el.find('.btn.action-apply').on('click', function (e) {
        if (extent_layer) {
          var $input = $(module.options.input)
          var geojson = {type: 'Polygon', coordinates: []}
          console.log ('Saving to target input '+($input.attr('id')))
          // Note: Unfortunately there is no leaflet method to convert a vector layer
          // to a geoJSON object (the inverse operation for L.geoJSON.geometryToLayer).
          var lonlats = []
          if (extent_layer.getLatLngs) {
            /* is a polygon */
            var points = extent_layer.getLatLngs()
            for (var i=0; i<points.length; i++) {
                lonlats.push ([points[i].lng, points[i].lat])
            }
          } else {
            var bounds = extent_layer.getBounds()
            var p1 = bounds.getSouthWest()
            var p2 = bounds.getNorthEast()
            lonlats = [[p1.lng, p1.lat], [p1.lng, p2.lat], [p2.lng, p2.lat], [p2.lng, p1.lat]]
          }
          geojson.coordinates.push(lonlats)
          console.debug (geojson)
          $input.val(JSON.stringify(geojson))
        }
        /* allow subsequent handlers (e.g. to dismiss modal dialog) */
        return true
      });  
    },

    _onRectCreated: function () {
        console.info ('A rectangle was created ...')
    },

    _onPolyCreated: function () {
        console.info ('A polygon/polyline was created ...') 
    },

  }
});

