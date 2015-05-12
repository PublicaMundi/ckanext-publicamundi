import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.model as model


log = logging.getLogger(__name__)


class AnalyticsPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

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

        map.connect("parse-services-access-count", "/api/analytics/parse/services",
                    controller=haparser_controller,
                    action='parse_services_access_count')
        map.connect("parse-bbox-access-count", "/api/analytics/parse/bbox",
                    controller=haparser_controller,
                    action='parse_bbox_access_count')
        map.connect("parse-coverage-access-count", "/api/analytics/parse/coverage/{coverage_name}",
                    controller=haparser_controller,
                    action='parse_coverage_access_count', coverage_name='{coverage_name}')
        map.connect("parse-coverages-access-count", "/api/analytics/parse/coverages",
                    controller=haparser_controller,
                    action='parse_used_coverages_count')
        map.connect("parse-bands-access-count", "/api/analytics/parse/bands/{coverage_name}",
                    controller=haparser_controller,
                    action='parse_band_access_count', coverage_name='{coverage_name}')
        map.connect("analytics", "/analytics", controller=analytics_controller, action='analytics')
        return map

    # IConfigurer

    def update_config(self, config):

        # Configure static resources
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-publicamundi-analytics')

        return

