from ckanext.publicamundi.analytics.controllers.util.habbox import HABbox
from ckanext.publicamundi.analytics.controllers.parsedinfo.habboxaccessinfo import HABboxAccessInfo
from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser


class HABboxAccessParser(HAParser):
    """
    Specialized HAParser for information about bounding boxes of coverages / layers accessed in the request.
    Limitations: currently assumes crs ESPG:3857.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, log_file_path):
        """
        Class constructor.
        :param <string> log_file_path: the path to the log file.
        """
        HAParser.__init__(self, log_file_path)

    def extract_wms_bbox(self, line):
        """
        Extracts the bounding box from a log line representing a wms request.
        :param <string> line: a log line representing a wms request.
        :return: <HABox>: the bbox corresponding to the line, None if not all the coordinates are given.
        """
        split = line.split(self.wms_bbox_key)
        if self.and_key in split[1]:
            focus = split[1].split(self.and_key)[0]
        else:
            focus = split[1].split(" ")[0]
        coordinates = focus.split(self.coordinates_separator)
        # check if the right number of coordinates has been parsed
        if len(coordinates) != 4:
            return None
        else:
            return HABbox(coordinates[0], coordinates[1], coordinates[2], coordinates[3])

    def extract_wcs_bbox(self, line):
        """
        Extracts the bounding box from a log line representing a wcs request.
        :param <string> line: a log line representing a wms request.
        :return: <HABox>: the bbox corresponding to the line, None if not all the coordinates are given.
        """
        # we need 2 subsets, one on each dimension
        split = line.split(self.wcs_bbox_key)
        if len(split) > 2:
            # take 1 and 2 and explode them again after = sign
            first_subset = split[1].split("=")[1].split("(")[1].split(")")[0].split(",")
            second_subset = split[2].split("=")[1].split("(")[1].split(")")[0].split(",")
            # check if we got exactly 4 points
            if len(first_subset) == 2 and len(second_subset) == 2:
                return HABbox(first_subset[0], second_subset[0], first_subset[1], second_subset[1])
        # in case we have the wrong number of points
        return None

    def parse_line(self, line):
        """
        Parses the information about bounding boxes addressed in a log line.
        :param <string> line: a log line representing a wms request.
        :return: <HABox>: the bbox corresponding to the line, None if not all the coordinates are given.
        """
        if self.wcs_bbox_key in line:
            return HABboxAccessInfo(self.extract_wcs_bbox(line), 1)
        if self.wms_bbox_key in line:
            return HABboxAccessInfo(self.extract_wms_bbox(line), 1)
        # in case there is no bbox
        return None

    def parse(self):
        """
        Parses the information about bounding boxes addressed in a log file.
        :return: <[HABoxAccessInfo]>: the list of bounding boxes addressed in the log file.
        """
        bbox_list = []
        with file(self.log_file_path) as f:
            for line in f.readlines():
                validated_line = self.validate_line(line)
                bbox = self.parse_line(validated_line)
                if bbox is not None:
                    bbox_list.append(bbox)
        return self.merge_info_list(bbox_list, HABboxAccessInfo.bbox_property_key)

    """
    Key definitions, to know what to look for in the log file.
    """
    wms_bbox_key = "bbox="
    wcs_bbox_key = "&subset"
    and_key = "&"
    coordinates_separator = ","
