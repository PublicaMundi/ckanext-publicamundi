import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.model as model


log = logging.getLogger(__name__)


class AnalyticsPlugin(p.SingletonPlugin):
    
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)

    def before_map(self, map):
        """
        Adds the url mappings to the analytics parser controller.
        The following urls are exposed:
        Analytics:

        /analytics        

        API:

        /api/analytics/parse/services: parses information about the access counts of the services (rasdaman, geoserver, w*s)
        /api/analytics/parse/bbox: parses information about the access counts of the accessed bounding boxes
        /api/analytics/parse/coverage/{coverage-name}: parses information about the coverage/layer with the passed name
        /api/analytics/parse/coverages: parses information about the access counts of all coverages/layers
        /api/analytics/parse/bands/{coverage-name}: parses information about the access count on bands for the
        coverage/layer with the passed name
        """
        controllers_base = "ckanext.publicamundi.analytics.controllers."
        haparser_controller = controllers_base + "haparsercontroller:HAParserController"
        analytics_controller = controllers_base + "analyticscontroller:AnalyticsController"

        map.connect("parse-services-access-count", "/api/analytics/services/{start_date}/{end_date}",
                    controller=haparser_controller,
                    action='parse_services_access_count', start_date='{start_date}', end_date='{end_date}')
        map.connect("parse-bbox-access-count", "/api/analytics/bbox/{start_date}/{end_date}",
                    controller=haparser_controller,
                    action='parse_bbox_access_count', start_date='{start_date}', end_date='{end_date}')
        map.connect("parse-coverage-access-count", "/api/analytics/coverage/{coverage_name}/{start_date}/{end_date}",
                    controller=haparser_controller,
                    action='parse_coverage_access_count', coverage_name='{coverage_name}', start_date='{start_date}',
                    end_date='{end_date}')
        map.connect("parse-coverages-access-count", "/api/analytics/coverages/{start_date}/{end_date}",
                    controller=haparser_controller,
                    action='parse_used_coverages_count', start_date='{start_date}', end_date='{end_date}')
        map.connect("parse-bands-access-count", "/api/analytics/bands/{coverage_name}/{start_date}/{end_date}",
                    controller=haparser_controller,
                    action='parse_band_access_count', coverage_name='{coverage_name}', start_date='{start_date}',
                    end_date='{end_date}')
        map.connect("analytics-api-adjust-workers", "/api/analytics/adjust/workers/{number}",
                    controller=analytics_controller, action='adjust_workers', number='{number}')
        map.connect("analytics-api-adjust-tiling", "/api/analytics/tiling/{coverage_name}/adjust",
                    controller=analytics_controller, action='adjust_tiling')
        map.connect("analytics-api-describe-tiling", "/api/analytics/tiling/{coverage_name}/describe",
                    controller=analytics_controller, action='describe_tiling')
        map.connect("analytics-api-adjust-cache", "/api/analytics/adjust/cache/{wcs}/{wms}",
                    controller=analytics_controller, action='adjust_cache', wcs='{wcs}', wms='{wms}')
        map.connect("analytics-api-adjust-pyramids", "/api/analytics/pyramids/{layer}/{level}",
                    controller=analytics_controller, action='adjust_pyramids', layer='{layer}', levels='{levels}')
        map.connect("analytics", "/analytics", controller=analytics_controller, action='analytics')
        return map

    ## IConfigurable interface ##
    
    def configure(self, config):

        # Setup analytics
        from ckanext.publicamundi.analytics.controllers import configmanager
        configmanager.setup(config)

        return

    ## IConfigurer interface ##

    def update_config(self, config):
        # Configure static resources
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-publicamundi-analytics')

        return

