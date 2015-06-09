/**
 * Creates a line graph.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */
FlancheJs.defineClass("Analytics.widgets.util.LineGraph", {
    /**
     * Class constructor.
     * @param title the title of the graph
     * @param valueField the name of the field in the dataSource which contains the grpah data.
     */
    init: function(title, valueField){
        this.setTitle(title);
        this.setValueField(valueField);
    },

    properties: {
        title: "",
        valueField: ""
    },

    methods: {
        /**
         * Returns an object describing an AmGraph.
         * @returns {*}
         */
        asAmGraph: function(){
            //set the title
            this._template.title = this.getTitle();
            //set the value field
            this._template.valueField = this.getValueField();
            return this._template;
        }
    },

    internals: {
        template: {
            "bullet": "round",
            "bulletBorderAlpha": 1,
            "bulletColor": "#FFFFFF",
            "bulletSize": 5,
            "hideBulletsCount": 50,
            "lineThickness": 2,
            "title": "$title$",
            "useLineColorForBulletBorder": true,
            "valueField": "$valueField"
        }
    }
})/**
 * Creates a column graph.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */
FlancheJs.defineClass("Analytics.widgets.util.ColumnGraph", {
    /**
     * Class constructor.
     * @param colorField the name of the field in the dataSource which contains the color of the column.
     * @param valueField the name of the field in the dataSource which contains the graph data.
     */
    init: function(colorField, valueField){
        this.setColorField(colorField);
        this.setValueField(valueField);
    },

    properties: {
        colorField: "",
        valueField: ""
    },

    methods: {
        /**
         * Returns an object describing an AmGraph.
         * @returns {*}
         */
        asAmGraph: function(){
            //set the title
            this._template.colorField = this.getColorField();
            //set the value field
            this._template.valueField = this.getValueField();
            return this._template;
        }
    },

    internals: {
        template: {
            "balloonText": "<b>[[category]]: [[value]]</b>",
            "colorField": "$colorField",
            "fillAlphas": 0.9,
            "lineAlpha": 0.2,
            "type": "column",
            "valueField": "$valueField"
        }
    }
})/**
 * Creates a line chart showing one or more graphs.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */

FlancheJs.defineClass("Analytics.widgets.LineChart", {

    /**
     * Class constructor.
     * @param selector the selector where the chart will be displayed
     * @param dataSource the datasource of the chart
     * @param titles the list of the titles of each graph displayed in this chart.
     * @param valueFields the key of the value field for each graph displayed in this chart.
     */
    init: function(selector, dataSource, titles, valueFields){
        this.setSelector(selector);
        this.setDataSource(dataSource);
        var graphs = [];
        for(var i = 0; i < titles.length; i++){
            graphs.push(new Analytics.widgets.util.LineGraph(titles[i], valueFields[i]));
        }
        this.setGraphs(graphs);
    },

    properties: {
        selector: "",
        dataSource: "",
        graphs: []
    },

    methods: {
        /**
         * Creates and renders the chart.
         */
        render: function () {
            var self = this;
            var chart = AmCharts.makeChart(self.getSelector(), {
                "type": "serial",
                "theme": "none",
                "pathToImages": "/vendor/amcharts/amcharts/images/",
                "dataDateFormat": "YYYY-MM-DD",
                "valueAxes": [{
                    "id": "v1",
                    "axisAlpha": 0,
                    "position": "left"
                }],
                "graphs": self.getGraphs().map(function(e){return e.asAmGraph()}),
                "chartScrollbar": {
                    "scrollbarHeight": 30
                },
                "chartCursor": {
                    "cursorPosition": "mouse",
                    "pan": true,
                    "valueLineEnabled": true,
                    "valueLineBalloonEnabled": true
                },
                "categoryField": "date",
                "categoryAxis": {
                    "parseDates": true,
                    "dashLength": 1,
                    "minorGridEnabled": true,
                    "position": "top"
                },
                "legend": {},
                "dataProvider": self.getDataSource()
            });

            chart.addListener("rendered", zoomChart);

            zoomChart();
            function zoomChart() {
                chart.zoomToIndexes(chart.dataProvider.length - 40, chart.dataProvider.length - 1);
            }
        }
    }
})
/**
 * Creates a column showing one or more graphs.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */

FlancheJs.defineClass("Analytics.widgets.ColumnChart", {
    /**
     * Class constructor.
     * @param selector the selector where the chart will be displayed
     * @param dataSource the datasource of the chart
     * @param title the list of the title of the graph displayed in this chart.
     * @param valueField the key of the value field for the graph displayed in this chart.
     */
    init: function(selector, dataSource, colorField, valueField, categoryField, coverageName){
        this.setSelector(selector);
        this.setDataSource(dataSource);
        this.setGraph(new Analytics.widgets.util.ColumnGraph(colorField, valueField));
        this.setCategoryField(categoryField);
        this.setCoverageName(coverageName);
    },

    properties: {
        selector: "",
        dataSource: "",
        graph: {},
        categoryField: "",
        coverageName: ""
    },

    methods: {
        /**
         * Creates and renders the chart.
         */
        render: function () {
            var self = this;
            var chart = AmCharts.makeChart(self.getSelector(), {
                "type": "serial",
                "theme": "none",
                "pathToImages":"/vendor/amcharts/amcharts/images/",
                "dataProvider": self.getDataSource(),
                "valueAxes": [{
                    "axisAlpha": 0,
                    "position": "left",
                    "title": ""
                }],
                "startDuration": 1,
                "graphs": [self.getGraph().asAmGraph()],
                "chartCursor": {
                    "categoryBalloonEnabled": false,
                    "cursorAlpha": 0,
                    "zoomable": false
                },
                "categoryField": self.getCategoryField(),
                "categoryAxis": {
                    "gridPosition": "start",
                    "labelRotation": 45,
                    "title": "Coverage " + self.getCoverageName() + " access statistics by band."
                }
            });
        }
    }
})/**
 * Creates a widget for displaying the most accessed coverages.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */
FlancheJs.defineClass("Analytics.widgets.CoverageAccess", {

    /**
     * Class constructor.
     * @param selector the place where the widget is to be displayed.
     * @param dataSource the data source for the graph.
     * @param coverageNameKey the key for the coverage name in the data source.
     * @param accessCountKey the key for access count in the data source.
     */
    init: function (selector, dataSource, coverageNameKey, accessCountKey) {
        this.setSelector(selector);
        this.setDataSource(dataSource);
        this.setCoverageNameKey(coverageNameKey);
        this.setAccessCountKey(accessCountKey);
        //set defaults
        this.setButtonDateGraphClass("coverage-access-date-graph-button");
        this.setButtonBandGraphClass("coverage-access-band-graph-button");
    },

    properties: {
        selector: "",
        tableHtml: "",
        rowsHtml: "",
        coverageNameKey: "",
        accessCountKey: "",
        dataSource: [],
        buttonDateGraphClass: "coverage-access-date-graph-button",
        buttonBandGraphClass: "coverage-access-band-graph-button"
    },

    methods: {
        /**
         * Renders a table with the coverage access counts.
         */
        render: function () {
            this._makeTableHtml();
            var element = document.getElementById(this.getSelector());
            element.innerHTML = this.getTableHtml();
        }
    },

    internals: {
        tHead: "<tr><th>Coverage Name</th><th>Access Count</th><th>Operations</th></tr>",
        row: '<tr><td>$name$</td><td>$count$</td><td>' +
                '<button data-coverageId="$name$" title="View access count by date" type="button" class="$btn-date-class$ btn btn-default btn-lg"> <span class="icon icon-calendar" aria-hidden="true"></span></button>' +
                '<button data-coverageId="$name$" title="View access count by band" type="button" class="$btn-band-class$ btn btn-default btn-lg"> <span class="icon icon-align-left rotate-90" aria-hidden="true"></span></button>' +
             '</td></tr>',
        template: "<table class='table table-striped'> <thead>$head$</thead><tbody>$rows$</tbody> </table>",
        makeTableHtml: function () {
            this._makeRowsHtml();
            var tableHtml = this._template.replace("$rows$", this.getRowsHtml())
                .replace("$head$", this._tHead);
            this.setTableHtml(tableHtml);
        },
        makeRowsHtml: function () {
            var rowsHtml = "";
            for (var i = 0; i < this.getDataSource().length; i++) {
                rowsHtml += this._row.replace(/\$name\$/g, this.getDataSource()[i][this.getCoverageNameKey()])
                    .replace("$count$", this.getDataSource()[i][this.getAccessCountKey()])
                    .replace("$btn-date-class$", this.getButtonDateGraphClass())
                    .replace("$btn-band-class$", this.getButtonBandGraphClass());
            }
            this.setRowsHtml(rowsHtml);
        }
    }
})/**
 * Creates a widget for displaying the most accessed coverage bounding boxes on a map.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */
FlancheJs.defineClass("Analytics.widgets.Map", {
    /**
     * Class constructor.
     * @param selector the div where the map is going to be displayed.
     * @param dataSource the dataSource for the bounding boxes displayed on the map.
     * @param bBoxKey the key for the bounding box in the dataSource.
     * @param countKey the key for the access count in the dataSource.
     * @param crsKey the key for the crs in the dataSource.
     */
    init: function (selector, dataSource, bBoxKey, countKey, crsKey) {
        this.setSelector(selector);
        this.setDataSource(dataSource);
        this.setBBoxKey(bBoxKey);
        this.setCountKey(countKey);
        this.setCrsKey(crsKey);
        //add default layer
        this.setLayers(
            [new ol.layer.Tile({
                source: new ol.source.OSM()
            })]
        );
    },

    properties: {
        selector: "",
        dataSource: [],
        bBoxKey: "",
        countKey: "",
        crsKey: "",
        layers: []
    },

    methods: {
        /**
         * Creates the layers and the map, which is rendered at the given selector.
         */
        render: function () {
            //create the layers
            this._makeLayers();
            //create the map
            this._makeMap();
        }
    },

    internals: {
        /**
         * Computes the color of the box for a count value.
         * For now it sets transparency to 0.05*log(count), max 1
         */
        getBoxColor: function (count) {
            var alpha = 1;
            if (1 || count < 20) {
                alpha = 0.05 * Math.log(count);
            }
            return {
                stroke: 'rgb(255, 255, 0)',
                fill: 'rgba(255, 255, 0, ' + alpha + ' )'
            };
        },
        /**
         * Creates a layer for every bbox indicated in the dataSource
         */
        makeLayers: function () {
            for (var i = 0; i < this.getDataSource().length; i++) {
                var currentEntry = this.getDataSource()[i];
                var bbox = currentEntry[this.getBBoxKey()];
                var count = currentEntry[this.getCountKey()];
                var crs = currentEntry[this.getCrsKey()];
                var color = this._getBoxColor(count);

                var style = [new ol.style.Style({
                    stroke: new ol.style.Stroke({
                        color: color.stroke,
                        width: 1
                    }),
                    fill: new ol.style.Fill({
                        color: color.fill
                    })
                })];
                var vectorSource = new ol.source.GeoJSON(
                    /** @type {olx.source.GeoJSONOptions} */ ({
                        object: {
                            'type': 'FeatureCollection',
                            'crs': {
                                'type': 'name',
                                'properties': {
                                    'name': 'EPSG:3857'
                                }
                            },
                            'features': [
                                {
                                    'type': 'Feature',
                                    'geometry': {
                                        'type': 'Polygon',
                                        'coordinates': bbox
                                    }
                                }
                            ]
                        }
                    }));

                this.getLayers().push(new ol.layer.Vector({
                    source: vectorSource,
                    style: style
                }));
            }
        },
        makeMap: function () {
            var map = new ol.Map({
                layers: this.getLayers(),
                target: this.getSelector(),
                controls: ol.control.defaults({
                    attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                        collapsible: false
                    })
                }),
                view: new ol.View({
                    center: [0, 0],
                    zoom: 2
                })
            });
        }
    }
})
