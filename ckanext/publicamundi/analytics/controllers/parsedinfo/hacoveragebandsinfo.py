from sqlalchemy import Column, Integer, Date, String
from ckanext.publicamundi.analytics.controllers.configmanager import ConfigManager, Base


class HACoverageBandsInfo(Base):
    """
    Keeps information about a specific coverage.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"
    __tablename__ = "coverage_bands"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    coverage_name = Column(String, nullable=False)
    band_name = Column(String, nullable=False)
    access_count = Column(Integer, nullable=False)
    color = Column(String, nullable=False)

    def __init__(self, date, coverage_name, band_name, access_count=0, color=""):
        """
        Class constructor
        :param <string> band_name: the name of the band for this entry.
        :param <int> access_count: how many ties the band has been accessed.
        :param <string> color: the color to be displayed for this band.
        """
        self.date = date
        self.coverage_name = coverage_name
        self.band_name = band_name
        self.access_count = access_count
        self.color = color

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += '"' + self.date_key + '"' + ":\"" + self.date.strftime(ConfigManager.export_date_format) + "\","
        output += '"' + self.coverage_name_key + '"' + ":\"" + self.coverage_name + "\","
        output += '"' + self.band_name_key + '"' + ":\"" + self.band_name + "\","
        output += '"' + self.access_count_key + '"' + ":" + str(self.access_count) + ","
        output += '"' + self.color_key + '"' + ":\"" + self.color + "\""
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The band and color are taken from the current object.
        The access counts are summed.
        :param <HACoverageInfo> another: an object to be merged with the current one.
        :return <HASCoverageInfo>: the merged object.
        """
        ret = HACoverageBandsInfo(self.date, self.coverage_name, self.band_name)
        ret.access_count = self.access_count + another.access_count
        ret.color = self.color
        return ret

    """
    Keys for exporting to json.
    """
    date_key = "date"
    coverage_name_key = "coverageName"
    band_name_key = "bandName"
    access_count_key = "accessCount"
    color_key = "color"
    # indicates the key after which the merging is done
    band_property_key = "band_name"
