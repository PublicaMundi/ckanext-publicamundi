/**
 * Creates a line graph.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */
FlancheJs.defineClass("Analytics.widgets.util.LineGraph", {
    /**
     * Class constructor.
     * @param title the title of the graph
     * @param valueField the name of the field in the dataSource which contains the graph data.
     */
    init: function (title, valueField) {
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
        asAmGraph: function () {
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
})
/**
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
    init: function (colorField, valueField) {
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
        asAmGraph: function () {
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
})
/**
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
    init: function (selector, dataSource, titles, valueFields) {
        this.setSelector(selector);
        this.setDataSource(dataSource);
        var graphs = [];
        for (var i = 0; i < titles.length; i++) {
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
                "graphs": self.getGraphs().map(function (e) {
                    return e.asAmGraph()
                }),
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
    init: function (selector, dataSource, colorField, valueField, categoryField, coverageName) {
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
                "pathToImages": "/vendor/amcharts/amcharts/images/",
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
})
/**
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
        this.setButtonPyramidsGraphClass("coverage-pyramids-button");
    },

    properties: {
        selector: "",
        tableHtml: "",
        rowsHtml: "",
        coverageNameKey: "",
        accessCountKey: "",
        dataSource: [],
        buttonDateGraphClass: "coverage-access-date-graph-button",
        buttonBandGraphClass: "coverage-access-band-graph-button",
        buttonPyramidsGraphClass: "coverage-pyramids-button"
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
        tHead: "<tr><th>Coverage Name</th><th>Access Count</th><th style='width:160px'>Operations</th></tr>",
        row: '<tr><td>$name$</td><td>$count$</td><td>' +
        '<button data-coverageId="$name$" title="View access count by date" type="button" class="$btn-date-class$ btn btn-default btn-lg"> <span class="icon icon-calendar" aria-hidden="true"></span></button>' +
        '<button data-coverageId="$name$" title="View access count by band" type="button" class="$btn-band-class$ btn btn-default btn-lg"> <span class="icon icon-align-left rotate-90" aria-hidden="true"></span></button>' +
        '<button data-coverageId="$name$" title="Generate pyramids" type="button" class="generate-pyramids $btn-band-class$ btn btn-default btn-lg"> <span class="icon icon-adjust rotate-90" aria-hidden="true"></span></button>' +
        '<button data-coverageId="$name$" title="Retile coverage" type="button" class="retile-coverage $btn-band-class$ btn btn-default btn-lg"> <span class="icon icon-barcode rotate-90" aria-hidden="true"></span></button>' +
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
});
/**
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
            var alpha = 0.7
            return {
                stroke: this._getColor(count) + ' 1)',
                fill: this._getColor(count) + alpha + ' )'
            };
        },

        getPercentage: function (value) {
            if (!this._max) {
                this._max = -1;
                for (var i = 0; i < this.getDataSource().length; i++) {
                    var count = this.getDataSource()[i][this.getCountKey()];
                    if (count > this._max) {
                        this._max = count
                    }
                }
            }
            return value / this._max
        },

        getColor: function (d) {
            d = this._getPercentage(d);
            return d > 0.92 ? 'rgba(128, 0, 38,' :
                d > 0.80 ? 'rgba(189, 0, 38, ' :
                    d > 0.60 ? 'rgba(227, 26, 28,' :
                        d > 0.40 ? 'rgba(252, 78, 42,' :
                            d > 0.20 ? 'rgba(253, 141, 60, ' :
                                d > 0.10 ? 'rgba(254, 178, 76,' :
                                    d > 0.05 ? 'rgba(254, 217, 118, ' :
                                        'rgba(255, 237, 160, ';
        },
        /**
         * Creates a layer for every bbox indicated in the dataSource
         */
        makeLayers: function () {
            for (var i = 0; i < this.getDataSource().length && i < 30; i++) {
                var currentEntry = this.getDataSource()[i];
                var bbox = currentEntry[this.getBBoxKey()];
                var count = currentEntry[this.getCountKey()];
                var crs = currentEntry[this.getCrsKey()];
                var color = this._getBoxColor(count);
                var coverage_name = currentEntry.coverage_name
                if (coverage_name) {
                    color = {
                        stroke: "#000",
                        fill: "rgba(255, 237, 160, 0.7)"
                    };
                    if (coverage_name == "Area of Interest") {
                        color = {
                            stroke: "#000",
                            fill: "rgba(128, 0, 38, 0.7)"
                        };
                    }
                }
                var style = [new ol.style.Style({
                    stroke: new ol.style.Stroke({
                        color: color.stroke,
                        width: 1
                    }),
                    fill: new ol.style.Fill({
                        color: color.fill
                    }),
                    text: new ol.style.Text({
                        textAlign: "center",
                        textBaseline: "middle",
                        font: "bold 12px Verdana",
                        text: coverage_name ? coverage_name : count.toString(),
                        fill: new ol.style.Fill({color: "#000"}),
                        stroke: new ol.style.Stroke({color: "#fff", width: 3}),
                        offsetX: 0,
                        offsetY: 0,
                        rotation: 0
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
});

var analyticsGetURLParameter = function (name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null
};

FlancheJs.defineClass("Analytics.widget.PeriodPicker", {
    init: function () {
    },

    statics: {
        startDate: new Date(),
        endDate: new Date(),
        formatDate: function (date) {
            return date.toISOString().slice(0, 10)
        }
    },

    methods: {
        initDatePickers: function () {
            $("#from-date-input").datepicker();
            var fromDate = new Date(), endDate = new Date();
            fromDate.setDate(fromDate.getDate() - 7);
            if (analyticsGetURLParameter("start")) {
                fromDate = new Date(analyticsGetURLParameter("start"))
            }
            if (analyticsGetURLParameter("end")) {
                endDate = new Date(analyticsGetURLParameter("end"))
            }
            $("#from-date-input").datepicker("setValue", fromDate);
            $("#to-date-input").datepicker();
            $("#to-date-input").datepicker("setValue", endDate);
            Analytics.widget.PeriodPicker.startDate = fromDate;
            Analytics.widget.PeriodPicker.endDate = endDate;
        },

        predefinedPeriodAction: function () {
            $("#predefined-period").change(function () {
                var val = $(this).val();
                var fromDate = new Date(), toDate = new Date();
                if (val == "day") {
                    fromDate.setDate(fromDate.getDate() - 1)
                }
                if (val == "week") {
                    fromDate.setDate(fromDate.getDate() - 7)
                }
                if (val == "month") {
                    fromDate.setDate(fromDate.getDate() - 31)
                }
                if (val == "year") {
                    fromDate.setDate(fromDate.getDate() - 365)
                }
                $("#from-date-input").datepicker("setValue", fromDate);
                $("#to-date-input").datepicker("setValue", toDate);
            })
        },

        dateChangeAction: function () {
            $('#from-date-input').datepicker()
                .on('changeDate', function (ev) {
                    Analytics.widget.PeriodPicker.startDate = ev.date
                });
            $('#to-date-input').datepicker()
                .on('changeDate', function (ev) {
                    Analytics.widget.PeriodPicker.endDate = ev.date
                });
        },

        run: function () {
            this.initDatePickers();
            this.dateChangeAction();
            this.predefinedPeriodAction();
        }
    }
});


FlancheJs.defineClass("Analytics.management.Manager", {
    init: function () {

    },

    statics: {
        saveModalFunction: "none",
        saveModalData: null,
        callbackError: function (message) {
            $("#analytics-modal .modal-title").html("Error");
            if (!message || !(typeof message === "string")) {
                message = "Could not perform action. Is the analytics service down?"
            }
            $("#analytics-modal .modal-body").html('<div class="alert alert-error" role="alert">' + message + '</div>');
            $("#analytics-modal").modal("show")
        }
    },

    methods: {
        adjustWorkersAction: function () {
            var self = this;
            jQuery("#worker-process").on("click", function () {
                jQuery.get("/api/analytics/adjust/workers/0").done(function (data) {
                    $("#analytics-modal").modal("show");
                    data = parseInt(data, 10)
                    $("#analytics-modal .modal-title").html("Adjust number of worker servers.");
                    $("#analytics-modal .modal-body").html("The number of worker servers should be adjusted to " + data +
                    " according to the usage pattern. Please confirm the change in the number of worker servers")
                    $("#analytics-modal").addClass("workers");
                    self.saveModalFunction = "workers"
                    self.saveModalData = data
                }).fail(Analytics.management.Manager.callbackError)
            })
        },
        adjustCacheAction: function () {
            var self = this;
            jQuery("#service-cache").on("click", function () {
                jQuery.get("/api/analytics/adjust/cache/0/0").done(function (data) {
                    $("#analytics-modal").modal("show");
                    var results = JSON.parse(data)
                    $("#analytics-modal .modal-title").html("Adjust the cache level of the OGC services.");
                    $("#analytics-modal .modal-body").html("The cache level will be adjusted according to the usage patterns to the following settings:<br/>" +
                    "<span class='label label-important'>WCS: " + results[0] + " MB</span><br/>" +
                    "<span class='label label-important'>WMS: " + results[1] + " MB</span><br/>" +
                    "Please confirm the change in the number of worker servers")
                    $("#analytics-modal").addClass("cache");
                    self.saveModalFunction = "cache"
                    self.saveModalData = results
                }).fail(Analytics.management.Manager.callbackError)
            })
        },

        retileAction: function () {
            var self = this;
            jQuery(document).on("click", ".retile-coverage", function () {
                var coverage_name = this.dataset.coverageid;
                jQuery.get("/api/analytics/tiling/" + coverage_name + "/describe").done(function (data) {
                    var response = JSON.parse(data);
                    if (response.error == true) {
                        self.callbackError("The coverage could not be retiled. Please check that the coverage is served by rasdaman WCS service and that the service is up and running.")
                    }
                    else {
                        $("#analytics-modal .modal-title").html("Retiling options for " + coverage_name);
                        $("#analytics-modal .modal-body").html("The coverage will be retiled to optimize for access on the following bounding boxes: <br/>" +
                        self.bboxesToString(response.info.bbox) + "<div id='retile-map'></div>");
                        $("#analytics-modal").modal("show");
                        self.createMap(coverage_name, response.info.coverage_bbox, response.info.bbox)
                        self.saveModalFunction = "retile";
                        self.saveModalData = coverage_name
                    }
                }).fail(Analytics.management.Manager.callbackError)
            })
        },

        generatePyramidsAction: function () {
            var self = this;
            jQuery(document).on("click", ".generate-pyramids", function () {
                var coverage_name = this.dataset.coverageid;
                $("#analytics-modal .modal-title").html("Generate pyramids for layer " + coverage_name)
                var options = ""
                for (var i = 1; i < 15; i++) {
                    options += "<option " + (i == 7 ? "selected" : "") + " value='" + i + "'>" + i + (i == 7 ? " (recommended)" : "") + "</option>"
                }
                $("#analytics-modal .modal-body").html("Please select the number of pyramid levels:<br/><select id='pyramid-levels' class='form-control'>" + options + "</select>");
                $("#analytics-modal").modal("show");
                self.saveModalFunction = "pyramids";
                self.saveModalData = {"coverage": coverage_name, "levels": jQuery("#pyramid-levels").val()}
            })
        },

        modalSaveAction: function () {
            var self = this;
            jQuery("#analytics-modal #save").on("click", function () {
                if (self.saveModalFunction == "workers") {
                    jQuery.get("/api/analytics/adjust/workers/" + self.saveModalData).done(function () {
                        self.displaySaveSuccess()
                    }).fail(Analytics.management.Manager.callbackError)
                }
                if (self.saveModalFunction == "cache") {
                    jQuery.get("/api/analytics/adjust/workers/" + self.saveModalData[0] + "/" + self.saveModalData[1]).done(function () {
                        self.displaySaveSuccess()
                    }).fail(Analytics.management.Manager.callbackError)
                }
                if (self.saveModalFunction == "retile") {
                    jQuery.get("/api/analytics/tiling/" + self.saveModalData + "/adjust").done(function () {
                        self.displaySaveSuccess()
                    }).fail(Analytics.management.Manager.callbackError)
                }
                if (self.saveModalFunction == "pyramids") {
                    jQuery.get("/api/analytics/pyramids/" + self.saveModalData.coverage + "/" + self.saveModalData.levels).done(function () {
                        self.displaySaveSuccess()
                    }).fail(Analytics.management.Manager.callbackError)
                }
            })
        },

        createMap: function (coverage_name, coverage_bbox, aoi_bboxes) {
            if (coverage_bbox[0] < 180 && coverage_bbox[3] > -180) {
                coverage_bbox = [coverage_bbox[1] * 0.999, coverage_bbox[0] * 0.999, coverage_bbox[3] * 0.999, coverage_bbox[2] * 0.999];
                coverage_bbox = ol.proj.transform(coverage_bbox, 'EPSG:4326', 'EPSG:3857')
            }

            var coverage_coordinates = [[coverage_bbox[0], coverage_bbox[1]], [coverage_bbox[2], coverage_bbox[1]], [coverage_bbox[2], coverage_bbox[3]], [coverage_bbox[0], coverage_bbox[3]]];
            var min_x = Number.MAX_VALUE, max_x = Number.MIN_VALUE, min_y = Number.MAX_VALUE, max_y = Number.MIN_VALUE;
            for (var i = 0; i < aoi_bboxes.length; i++) {
                var aoib = aoi_bboxes[i];
                if (aoib[0] < 180 && aoib[3] > -180) {
                    aoib = ol.proj.transform(aoib, 'EPSG:4326', 'EPSG:3857');
                }
                min_x = aoib[0] < min_x ? aoib[0] : min_x;
                min_y = aoib[1] < min_y ? aoib[1] : min_y;
                max_x = aoib[2] > max_x ? aoib[2] : max_x;
                max_y = aoib[3] > max_y ? aoib[3] : max_y;
            }
            var aoi = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]];
            var map = new Analytics.widgets.Map("retile-map", [
                {
                    "accessCount": 50,
                    "bbox": [coverage_coordinates],
                    "crs": "",
                    coverage_name: coverage_name
                },
                {
                    "accessCount": 100,
                    bbox: [aoi],
                    "crs": "",
                    "coverage_name": "Area of Interest"
                }], "bbox", "accessCount", "crs");
            map.render()
        },


        bboxesToString: function (bboxes) {
            var bbs = bboxes.map(function (bbox) {
                return "<li><span class='label label-info'>[" + bbox[0] + ":" + bbox[2] +
                    "," + bbox[1] + ":" + bbox[3] + "]</span></li>"
            });
            return "<ul>" + bbs.join("\n") + "</ul>"
        },

        displaySaveSuccess: function () {
            $("#analytics-modal .modal-body").html('<div class="alert alert-success" role="alert">The action was performed successfully</div>')
            $("#save").hide();
            setTimeout(function () {
                $("#analytics-modal").modal("hide")
                $("#save").show()
            }, 2000)
        },

        run: function () {
            this.adjustWorkersAction();
            this.adjustCacheAction();
            this.retileAction();
            this.generatePyramidsAction();
            this.modalSaveAction();
        }
    }
});