from ckanext.publicamundi.analytics.controllers.configmanager import ConfigManager
from ckanext.publicamundi.analytics.controllers.parsers.habboxaccessparser import HABboxAccessParser
from ckanext.publicamundi.analytics.controllers.parsers.hacoverageaccessparser import HACoverageAccessParser
from ckanext.publicamundi.analytics.controllers.parsers.hacoveragebandparser import HACoverageBandParser
from ckanext.publicamundi.analytics.controllers.parsers.haservicesaccessparser import HAServicesAccessParser
from ckanext.publicamundi.analytics.controllers.parsers.hausedcoveragesparser import HAUsedCoveragesParser
from ckan.lib.base import BaseController
from ckan.lib.base import(
    BaseController, c, request, session, render, config, abort)

class HAParserController(BaseController):
    """
    Offers an API for calling specialized parsers.
    The following methods are exposed:
    /api/analytics/parse/services: parses information about the access counts of the services (rasdaman, geoserver, w*s)
    /api/analytics/parse/bbox: parses information about the access counts of the accessed bounding boxes
    /api/analytics/parse/coverage/{coverage-name}: parses information about the coverage/layer with the passed name
    /api/analytics/parse/coverages: parses information about the access counts of all coverages/layers
    /api/analytics/parse/bands/{coverage-name}: parses information about the access count on bands for the
    coverage/layer with the passed name
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def parse_services_access_count(self):
        """
        Parses information about the access counts of the services (rasdaman, geoserver, w*s).
        """
        parser = HAServicesAccessParser(ConfigManager.log_file_path)
        return parser.print_as_json_array(parser.parse())

    def parse_bbox_access_count(self):
        """
        Parses information about the access counts of the accessed bounding boxes.
        """
        parser = HABboxAccessParser(ConfigManager.log_file_path)
        return parser.print_as_json_array(parser.parse())

    def parse_coverage_access_count(self, coverage_name):
        """
        Parses information about the coverage/layer with the passed name.
        :param <string> coverage_name: the coverage/layer name to be analyzed.
        """
        parser = HACoverageAccessParser(ConfigManager.log_file_path, coverage_name)
        return parser.print_as_json_array(parser.parse())

    def parse_used_coverages_count(self):
        """
        Parses information about the access counts of all coverages/layers.
        """
        parser = HAUsedCoveragesParser(ConfigManager.log_file_path)
        return parser.print_as_json_array(parser.parse())

    def parse_band_access_count(self, coverage_name):
        """
        Parses information about the access count on bands for the coverage/layer with the passed name.
        :param <string> coverage_name: the coverage/layer name to be analyzed.
        """
        parser = HACoverageBandParser(ConfigManager.log_file_path, coverage_name)
        return parser.print_as_json_array(parser.parse())
