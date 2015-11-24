from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckanext.publicamundi.analytics.controllers.parsedinfo.hacoverageaccessinfo import HACoverageAccessInfo


class HACoverageAccessParser(HAParser):
    """
    Specialized HAParser for information about a specific coverage.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, coverage_name):
        """
        Class constructor.
        :param <string> log_file_path: the path to the log file
        :param <string> coverage_name: the name of the coverage to be searched for.
        """
        HAParser.__init__(self)
        self.coverage_name = coverage_name.lower()

    def parse_coverage_access_line(self, line):
        """
        Creates a HACoverageAccessInfo object from a line which already contains the coverage name.
        :param <string> line: the line containing the coverage name.
        :return: <HACoverageAccessInfo> object representing the entry.
        """
        coverage_access_info = HACoverageAccessInfo(self.parse_date(line), 1)
        return coverage_access_info

    def parse(self):
        """
        Parses the log files an returns information about the current coverage accesses, by date.
        :return: <[HaCoverageInfo]> a list of objects containing access information for the current coverage,
        one for each unique date.
        """
        access_info_list = []
        for filename in self.log_files:
            with file(filename) as f:
                # simply check how many requests contain the coverage or layer name
                for line in f.readlines():
                    validated_line = self.validate_line(line)
                    if self.coverage_name in validated_line:
                        access_info_list.append(self.parse_coverage_access_line(validated_line))
        return self.merge_info_list(access_info_list)
