class HACoverageBandInfo:
    """
    Keeps information about a specific coverage.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, band_name, access_count=0, color=""):
        """
        Class constructor
        :param <string> band_name: the name of the band for this entry.
        :param <int> access_count: how many ties the band has been accessed.
        :param <string> color: the color to be displayed for this band.
        """
        self.band_name = band_name
        self.access_count = access_count
        self.color = color

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += self.band_name_key + ":\"" + self.band_name + "\","
        output += self.access_count_key + ":" + str(self.access_count) + ","
        output += self.color_key + ":\"" + self.color + "\""
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The band and color are taken from the current object.
        The access counts are summed.
        :param <HACoverageInfo> another: an object to be merged with the current one.
        :return <HASCoverageInfo>: the merged object.
        """
        ret = HACoverageBandInfo(self.band_name)
        ret.access_count = self.access_count + another.access_count
        ret.color = self.color
        return ret

    """
    Keys for exporting to json.
    """
    band_name_key = "bandName"
    access_count_key = "accessCount"
    color_key = "color"
    # indicates the key after which the merging is done
    band_property_key = "band_name"
