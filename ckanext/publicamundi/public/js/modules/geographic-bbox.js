(function () {
 
    var debug = $.proxy(window.console, 'debug'),
        warn = $.proxy(window.console, 'warn'),
        assert = $.proxy(window.console, 'assert')
    
    var config = {
        leaflet: {
            createOptions: {
                attributionControl: false,
            },
            baseLayer: {
                // Provide base map from MapQuest - OpenStreetMap
                url: 'http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
                params: { maxZoom: 18, subdomains: '1234' },
            },
            styles: {
                drawRectangle: {
                    color: '#F06F64',
                    weight: 2,
                    opacity: 1,
                    fillColor: '#F06F64',
                    fillOpacity: 0.1
                },
            },
        },
        dialog: { 
            container: '#content .wrapper',
            id: 'draw-bbox-dialog',
            template: 'draw-bbox-dialog.html',
        },
        extent: {
            type: 'Polygon',
            coordinates: [
                [
                    [19.190674, 34.800395], [30.264893, 34.800395],
                    [30.264893, 41.82466], [19.190674, 41.82466],
                    [19.190674, 34.800395]
                ]
            ]
        },
    };
    
    var $container = $(config.dialog.container)
    
    var map1 = null

    this.ckan.module('input-geographic-bbox', function ($, _) {

        return {

            options: {
                qname: null,
                precision: 6,
            },
 
            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    sandbox = this.sandbox
                
                var $dialog = $container.find('#' + config.dialog.id)
                
                if (!$dialog.length) {
                    var tpl_vars = { id: config.dialog.id }
                    sandbox.client.getTemplate(config.dialog.template, tpl_vars, function (markup) {
                        $dialog = $(markup)
                            .modal({ show: false, keyboard: true })
                            .appendTo($container)
                            .on('shown', $.proxy(module._prepareMap, null))
                        $dialog.find('a.btn.apply')
                            .on('click', $.proxy(module._handleApply, null))
                        $dialog.find('a.btn.cancel')
                            .on('click', $.proxy(module._handleCancel, null))
                    })
                }
                
                $el.find('a.btn.draw-bbox').on('click', $.proxy(module._openDialog, module)) 
                
                debug('Initialized module: input-geographic-bbox opts=', this.options)
            },
 
            teardown: function () 
            { 
                debug('Tearing down module: input-geographic-bbox')
            },

            selectedLayer: null,

            _createMap: function ()
            {
                var $dialog = $container.find('#' + config.dialog.id)
                assert($dialog.length == 1) 

                var extent = new L.GeoJSON(config.extent)
                
                debug('Creating leaflet map ...')

                // Create map

                var map = new L.Map(config.dialog.id + '-map-container', 
                    config.leaflet.createOptions);
                            
                map.addLayer(new L.TileLayer(
                    config.leaflet.baseLayer.url, 
                    config.leaflet.baseLayer.params));

                // Initialize map controls
                
                map.addControl(new L.Control.Draw({
                    position: 'topright',
                    polyline: false,
                    polygon: false,
                    circle: false,
                    marker: false,
                    rectangle: {
                        shapeOptions: config.leaflet.styles.drawRectangle,
                        title: 'Draw a rectangle'
                    }
                }));

                map.fitBounds(extent.getBounds());
                
                // Bind draw-related event handlers

                var module = $dialog.data('current-module')
                
                map.on('draw:rectangle-created', $.proxy(module._recordRectangle, null));

                // Done
                return map
            },

            _openDialog: function () 
            {
                var module = this 
                 
                var $dialog = $container.find('#' + config.dialog.id)
                
                // Show and store reference to current module instance
                
                assert($dialog.data('current-module') == null)

                $dialog
                    .data('current-module', module)
                    .modal('show')

                return false
            },

            _closeDialog: function ()
            {
                var module = this 
                
                var $dialog = $container.find('#' + config.dialog.id)
                
                // Cleanup selected layers so that they dont interfer
                // with other instances of this module
                
                assert(map1 != null)
                
                if (module.selectedLayer) {
                    map1.removeLayer(module.selectedLayer)
                    module.selectedLayer = null
                }

                // Hide and cleanup reference to current module instance
                
                $dialog
                    .modal('hide')
                    .data('current-module', null)
                
                return false
            },

            _prepareMap: function ()
            {
                var $dialog = $container.find('#' + config.dialog.id)
                
                var module = $dialog.data('current-module')
                assert(module != null)
                
                // Initialize map (once)
                // Note that could not happen before, initialization must run
                // after the dialog is shown (in order to have the dimensions 
                // of its container).

                if (map1 == null) {
                    map1 = module._createMap()
                }
                assert(map1 != null)

                // If inputs are non-empty, try to construct a vector (rectangle)
                // layer from them (and overlay in map)

                var layer = module.getLayerFromInput()
                if (layer){
                    map1.addLayer(layer);
                    map1.fitBounds(layer.getBounds())
                    module.selectedLayer = layer
                }
                
                return true
            },

            _handleApply: function()
            {
                var $dialog = $container.find('#' + config.dialog.id)

                var module = $dialog.data('current-module')

                // Assign inputs (W-E latitude, S-N longitude)

                module.assignInput()
                
                // Cleanup and close

                return module._closeDialog()
            },

             _handleCancel: function()
            {
                var $dialog = $container.find('#' + config.dialog.id)

                var module = $dialog.data('current-module')
                
                // Cleanup and close

                return module._closeDialog()
            },
           
            _recordRectangle: function (ev)
            {
                var $dialog = $container.find('#' + config.dialog.id)
                
                var module = $dialog.data('current-module')

                var selected_layer = module.selectedLayer
                if (selected_layer) {
                    map1.removeLayer(selected_layer);
                }
                selected_layer = ev.rect;
                map1.addLayer(selected_layer);
                module.selectedLayer = selected_layer

                return false
            },

            getLayerFromInput: function ()
            {
                var module = this,
                    qname = this.options.qname,
                    layer = null,
                    geojson = null
                
                // Attempt to re-construct a layer from inputs
                var $inp = module.el.find('input')
                    .filter('[type=number]')
                    .filter('[name^="' + qname + '.' + '"]') 
                
                var wblng = parseFloat($inp.filter('[name$=wblng]').val()),
                    eblng = parseFloat($inp.filter('[name$=eblng]').val()),
                    sblat = parseFloat($inp.filter('[name$=sblat]').val()),
                    nblat = parseFloat($inp.filter('[name$=nblat]').val())

                if (!(isNaN(wblng) || isNaN(eblng) || isNaN(sblat) || isNaN(nblat))) {
                    geojson = { 
                        type: 'Polygon', 
                        coordinates: [[
                            [wblng, sblat], [wblng, nblat],
                            [eblng, nblat], [eblng, sblat],
                        ]] 
                    }
                    layer = new L.GeoJSON(geojson)
                }

                return layer
            },

            assignInput: function ()
            {
                var module = this, 
                    opts = this.options,
                    selected_layer = this.selectedLayer,
                    qname = opts.qname
                
                if (selected_layer) {
                    // Note: Unfortunately there is no leaflet method to convert a vector layer
                    // to a geoJSON object (the inverse operation for L.geoJSON.geometryToLayer).
                    var geojson = { type: 'Polygon', coordinates: null },
                        lonlats = null
                   
                    if ($.isFunction(selected_layer.getLatLngs)) {
                        // is a polygon 
                        var points = selected_layer.getLatLngs()
                        lonlats = []
                        for (var i = 0; i < points.length; i++) {
                            lonlats.push([points[i].lng, points[i].lat])
                        }
                    } else {
                        // is a plain rectangle
                        var bounds = selected_layer.getBounds(),
                            p1 = bounds.getSouthWest(),
                            p2 = bounds.getNorthEast()
                        lonlats = [
                            [p1.lng, p1.lat], [p1.lng, p2.lat],
                            [p2.lng, p2.lat], [p2.lng, p1.lat],
                        ]
                    }

                    geojson.coordinates = [lonlats]

                    // Assign to each input
                    
                    var prec = opts.precision, $inp = null
                    
                    $inp = module.el.find('input')
                        .filter('[type=number]')
                        .filter('[name^="' + qname + '.' + '"]') 
                    
                    $inp.filter('[name$=wblng]').val(lonlats[0][0].toFixed(prec))
                    $inp.filter('[name$=eblng]').val(lonlats[2][0].toFixed(prec))
                    $inp.filter('[name$=sblat]').val(lonlats[0][1].toFixed(prec))
                    $inp.filter('[name$=nblat]').val(lonlats[1][1].toFixed(prec))

                } else {
                    // noop: Nothing was selected
                }

                return true
            },
        };
    })

    this.ckan.module('compute-spatial-from-bbox', function ($, _) {
 
        return {
            options: {
                qname: null,
            },
 
            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options,
                    qname = opts.qname

                $el.closest('form').on('submit', function (ev) {
                    // Find all related inputs and form a geoJSON object
                    var $inp = $(this).find('input[name^="' + qname + '.' + '"]') 
                    
                    var wblng = parseFloat($inp.filter('[name$=wblng]').val()),
                        eblng = parseFloat($inp.filter('[name$=eblng]').val()),
                        sblat = parseFloat($inp.filter('[name$=sblat]').val()),
                        nblat = parseFloat($inp.filter('[name$=nblat]').val())
                    
                    if (!(isNaN(wblng) || isNaN(eblng) || isNaN(sblat) || isNaN(nblat))) {
                        var geojson = JSON.stringify({ 
                            type: 'Polygon', 
                            coordinates: [[
                                [wblng, sblat], [wblng, nblat],
                                [eblng, nblat], [eblng, sblat],
                                [wblng, sblat],
                            ]] 
                        })
                        $el.find('input[name=spatial]').val(geojson)
                    }

                    return true
                })               
                 
                debug('Initialized module: compute-spatial-from-bbox opts=', opts)
            },
 
            teardown: function () 
            { 
                debug('Tearing down module: compute-spatial-from-bbox')
            },
        };
    })

}).apply(this)  
