/**
 * Application orchestrator.
 * Creates and displays the analytics widgets.
 *
 * @author Vlad Merticariu<merticariu@rasdaman.com>
 */

var loadingGifUrl = "/loading.gif"
var loadingGif = "<img src=\"" + loadingGifUrl + "\" height=\"500\"/>";

var servicesUrl = "/api/analytics/parse/services";
var coverageAccessCountUrl = "/api/analytics/parse/coverage/{coverage_id}";
var bandAccessCount = "/api/analytics/parse/bands/{coverage_id}";
var coveragesUrl = "/api/analytics/parse/coverages";
var boundingBoxesUrl = "/api/analytics/parse/bbox";

/**
 * Creates the rasdaman access count chart.
 */
var makeRasdamanChart = function(servicesUrl){
    $.get(servicesUrl, function(response){      
        servicesDataSourceCache = eval(response);
        var chart = new Analytics.widgets.LineChart("rasdaman-access-graph", servicesDataSourceCache, ["rasdaman access count"], ["rasdaman"]);
        chart.render();
    })
};

/**
 * Creates the Geoserver access count chart.
 */
var makeGeoserverChart = function(servicesUrl){
    $.get(servicesUrl, function(response){      
        servicesDataSourceCache = eval(response);
        var chart = new Analytics.widgets.LineChart("geoserver-access-graph", servicesDataSourceCache, ["Geoserver access count"], ["geoserver"]);
        chart.render();
    })
};

/**
 * Creates the services access counts chart.
 */
var makeServicesChart = function(servicesUrl){
    $.get(servicesUrl, function(response){
        servicesDataSourceCache = eval(response);
        var chart = new Analytics.widgets.LineChart("services-access-graph", servicesDataSourceCache, ["WCS", "WCPS", "WMS"], ["rasdaman_wcs", "rasdaman_wcps", "rasdaman_wms"]);
        chart.render()  
    })  
};

/**
 * Creates the coverage access count chart.
 */
var makeCoverageAccessCountChart = function(coverageId, coverageAccessCountUrl){
    $("#coverage-access-graph").html(loadingGif);
    $.get(coverageAccessCountUrl.replace("{coverage_id}", coverageId), function(response){
      var dataSource = eval(response)
      var graphTitle = coverageId + " access count";
      var chart = new Analytics.widgets.LineChart("coverage-access-graph", dataSource, [graphTitle], ["accessCount"]);
      chart.render();
    })    
};

/**
 * Creates the band access count chart.
 */
var makeBandAccessCountChart = function(coverageId, bandAccessCount){
    $("#coverage-band-access-graph").html(loadingGif);
    $.get(bandAccessCount.replace("{coverage_id}", coverageId), function(response){
	var dataSource = eval(response)
        if(dataSource.length > 0){	
    	  var chart = new Analytics.widgets.ColumnChart("coverage-band-access-graph", dataSource, "color", "accessCount", "bandName", coverageId);
    	  chart.render();
        }
        else{
          $("#coverage-band-access-graph").html("<p>No band information for this coverage.</p>")
        }
    })
};

/**
 * Creates the table of coverages/layers, with the corresponding access counts.
 */
var makeCoverageAccessTable = function(coveragesUrl, coverageAccessCountUrl, bandAccessCount){
    $.get(coveragesUrl, function(response){
      var dataSource = eval(response);
      var table = new Analytics.widgets.CoverageAccess("coverage-access-table", dataSource, "id", "accessCount");
      table.render();

        // inititialize coverage graphs with first layer
        var firstCoverageId = $('.coverage-access-date-graph-button').first().data('coverageid');
        makeCoverageAccessCountChart(firstCoverageId, coverageAccessCountUrl);
        makeBandAccessCountChart(firstCoverageId, bandAccessCount);
        $('#coverage-access-date-title').html(firstCoverageId);
        $('#coverage-access-band-title').html(firstCoverageId);

      jQuery("." + table.getButtonDateGraphClass()).click(function(){
        makeCoverageAccessCountChart(this.dataset.coverageid, coverageAccessCountUrl);
        $('#coverage-access-date-title').html(this.dataset.coverageid);
         $('html, body').animate({
            scrollTop: $("#coverage-access-date-title").offset().top
        }, 1000);
      }) 
      jQuery("." + table.getButtonBandGraphClass()).click(function () {        
        makeBandAccessCountChart(this.dataset.coverageid, bandAccessCount);

        $('#coverage-access-band-title').html(this.dataset.coverageid);
        $('html, body').animate({
            scrollTop: $("#coverage-access-band-title").offset().top
        }, 1000);

      })
      //jQuery("." + table.getButtonDateGraphClass()).first().click()
      //jQuery("." + table.getButtonBandGraphClass()).first().click()
    })
}

/**
 * Creates the map displaying the accessed bounding boxes.
 */
var makeBoundingBoxesMap = function(boundingBoxesUrl){
    $.get(boundingBoxesUrl, function(response){
      var dataSource = eval(response)
      var map = new Analytics.widgets.Map("bounding-boxes-map", dataSource, "bbox", "accessCount", "crs");
      map.render();
    })    
}


makeRasdamanChart(servicesUrl);
makeGeoserverChart(servicesUrl);
makeServicesChart(servicesUrl);
makeCoverageAccessTable(coveragesUrl, coverageAccessCountUrl, bandAccessCount);
makeBoundingBoxesMap(boundingBoxesUrl);

$(".scroll-up-button").click(function(){
    $('html, body').animate({
            scrollTop: $("#coverage-access-table-container").offset().top
        }, 1000);
});
