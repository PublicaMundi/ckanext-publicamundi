from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckanext.publicamundi.analytics.controllers.parsedinfo.haserviceaccessinfo import HAServiceAccessInfo


class HAServicesAccessParser(HAParser):
    """
    Specialized HAParser for information about the services.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self):
        """
        Class constructor.
        :param <string> log_file_path: the path to the log file.
        """
        HAParser.__init__(self)

    def parse_service_info_line(self, line=""):
        """
        Parses the service information from one line of log.
        :param <string> line: the line to be parsed.
        :return: <HAServiceInfo> an object containing the services access counts and the date.
        """
        # start with parsing the date
        haservice_info = HAServiceAccessInfo(self.parse_date(line))
        # parse services information
        if self.rasdaman_key in line:
            haservice_info.rasdaman = 1
        if self.wcs_key in line:
            haservice_info.rasdaman_wcs = 1
        if self.wcps_key in line:
            haservice_info.rasdaman_wcps = 1
        if self.wms_key in line:
            haservice_info.rasdaman_wms = 1
        if self.geoserver_key in line:
            haservice_info.geoserver = 1
        return haservice_info

    def parse(self):
        """
        Parses the services access counts from the current log file.
        :return <[HAServiceInfo]> a list of objects representing the total services access counts for each different date.
        """
        services_info_list = []
        for filename in self.log_files:
            with file(filename) as f:
                for line in f.readlines():
                        # only consider valid lines.
                    validated_line = self.validate_line(line)
                    if validated_line:
                        services_info_list.append(self.parse_service_info_line(validated_line))
        # merge the results and return
        return self.merge_info_list(services_info_list)

    """
    Key definitions, to know what to look for in the log file.
    """
    rasdaman_key = "rasdaman"
    wcs_key = "service=wcs"
    wcps_key = "request=processcoverage"
    wms_key = "service=wms"
    geoserver_key = "geoserver"
