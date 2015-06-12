class HAUsedCoveragesInfo:
    """
    Keeps information about all accessed coverages.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, coverage_name, access_count):
        """
        Class constructor.
        :param <string> coverage_name: the coverage name for the current entry.
        :param <int> access_count: how many times the given coverage has been accessed.
        """
        self.coverage_name = coverage_name
        self.access_count = access_count

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += self.coverage_name_key + ":\"" + self.coverage_name + "\","
        output += self.access_count_key + ":" + str(self.access_count)
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The coverage_name is taken from the current object.
        The access counts are summed.
        :param <HACoverageInfo> another: an object to be merged with the current one.
        :return: <HASCoverageInfo>: the merged object.
        """
        ret = HAUsedCoveragesInfo(self.coverage_name, self.access_count + another.access_count)
        return ret

    """
    Keys for exporting to json.
    """
    coverage_name_key = "id"
    access_count_key = "accessCount"
    # indicates the key after which the merging is done
    coverage_name_property_key = "coverage_name"