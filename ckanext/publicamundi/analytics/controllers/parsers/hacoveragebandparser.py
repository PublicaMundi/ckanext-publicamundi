from ckanext.publicamundi.analytics.controllers.parsedinfo.hacoveragebandinfo import HACoverageBandInfo
from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser


class HACoverageBandParser(HAParser):
    """
    Specialized HAParser for information about specific bands of a coverage.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, coverage_name):
        """
        Class constructor.
        :param <string> log_file_path: the path to the log file.
        :param <string> coverage_name: the coverage for which the information is parsed.
        """
        HAParser.__init__(self)
        self.coverage_name = coverage_name.lower()

    def parse_coverage_band_line(self, line):
        """
        Parses a line in the log file which already contains the coverage.
        :param <string> line: a log line in which the searched coverage is addressed.
        :return: <[HACoverageBandInfo]> list of objects describing the bands accessed in the current line.
        """
        ret = []
        if self.range_subset_key in line.lower():
            split = line.split(self.range_subset_key)
            focus = split[1]
            # check if the range subset is given in the middle of the request or at the end
            if self.and_key in focus:
                # in the middle, do further split
                focus = focus.split(self.and_key)[0]
            else:
                # otherwise focus is at the end followed by a space
                focus = focus.split(" ")[0]
            # check if there are several bands accessed
            if self.comma_key in focus:
                bands = focus.split(self.comma_key)
            elif self.column_key in focus:
                bands = focus.split(self.column_key)
            else:
                bands = [focus]
            # add all the bands to the result
            for band in bands:
                ret.append(HACoverageBandInfo(band, 1))
        return ret

    def assign_colors_to_bands(self, band_info_list):
        """
        Assigns colors from the color_list to a list of HACoverageBandInfo objects.
        :param <[HACoverageBandInfo]> band_info_list: the list of objects to which colors are to be assigned.
        """
        i = 0
        for band_info in band_info_list:
            band_info.color = self.color_list[i % len(self.color_list)]
            i += 1

    def parse(self):
        """
        Parses the current log file and returns information about the bands that have been accessed.
        :return: <[HACoverageBandInfo]> a list of objects describing the bands accessed.
        """
        band_info_list = []
        for filename in self.log_files:
            with file(filename) as f:
                for line in f.readlines():
                    validated_line = self.validate_line(line)
                    if self.coverage_name in validated_line:
                        band_info_list += self.parse_coverage_band_line(validated_line)
        merged_list = self.merge_info_list(band_info_list, HACoverageBandInfo.band_property_key)
        self.assign_colors_to_bands(merged_list)
        return merged_list

    """
    Key definitions, to know what to look for in the log file.
    """
    range_subset_key = "rangesubset="
    and_key = "&"
    comma_key = ","
    column_key = ":"
    color_list = ["#FE2619", "#1CD52B", "#2462D4", "#2462D4", "#9423D2"]
