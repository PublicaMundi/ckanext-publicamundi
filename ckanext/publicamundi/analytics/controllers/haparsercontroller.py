from ckanext.publicamundi.analytics.controllers.dbservice.dbreader import DbReader
from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckan.lib.base import BaseController
from ckan.lib.base import(
    BaseController)


class HAParserController(BaseController):
    """
    Offers an API for calling specialized parsers.
    The following methods are posed:
    /api/analytics/parse/services: parses information about the access counts of the services (rasdaman, geoserver, w*s)
    /api/analytics/parse/bbox: parses information about the access counts of the accessed bounding boxes
    /api/analytics/parse/coverage/{coverage-name}: parses information about the coverage/layer with the passed name
    /api/analytics/parse/coverages: parses information about the access counts of all coverages/layers
    /api/analytics/parse/bands/{coverage-name}: parses information about the access count on bands for the
    coverage/layer with the passed name
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def parse_services_access_count(self, start_date, end_date):
        """
        Parses information about the access counts of the services (rasdaman, geoserver, w*s).
        """
        return HAParser.print_as_json_array(DbReader.read_service_access_by_date(start_date, end_date))

    def parse_bbox_access_count(self, start_date, end_date):
        """
        Parses information about the access counts of the accessed bounding boxes.
        """
        return HAParser.print_as_json_array(DbReader.read_bbox_access_totals(start_date, end_date))

    def parse_coverage_access_count(self, coverage_name, start_date, end_date):
        """
        Parses information about the coverage/layer with the passed name.
        :param <string> coverage_name: the coverage/layer name to be analyzed.
        """
        return HAParser.print_as_json_array(DbReader.read_coverage_access_by_date(coverage_name, start_date, end_date))

    def parse_used_coverages_count(self, start_date, end_date):
        """
        Parses information about the access counts of all coverages/layers.
        """
        return HAParser.print_as_json_array(DbReader.read_used_coverages_totals(start_date, end_date))

    def parse_band_access_count(self, coverage_name, start_date, end_date):
        """
        Parses information about the access count on bands for the coverage/layer with the passed name.
        :param <string> coverage_name: the coverage/layer name to be analyzed.
        """
        return HAParser.print_as_json_array(DbReader.read_coverage_bands_totals(coverage_name, start_date, end_date))