from sqlalchemy import Column, Integer, String, Date
from ckanext.publicamundi.analytics.controllers import configmanager

Base = configmanager.Base

class HAUsedCoveragesInfo(Base):
    """
    Keeps information about all accessed coverages.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"
    __tablename__ = "used_coverages"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    coverage_name = Column(String, nullable=False)
    access_count = Column(Integer, nullable=False)

    def __init__(self, date, coverage_name, access_count):
        """
        Class constructor.
        :param <string> coverage_name: the coverage name for the current entry.
        :param <int> access_count: how many times the given coverage has been accessed.
        """
        self.date = date
        self.coverage_name = coverage_name
        self.access_count = access_count

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += '"' + self.date_key + '"' + ":\"" +\
            self.date.strftime(configmanager.export_date_format) + "\","
        output += '"' + self.coverage_name_key + '"' + ":\"" + self.coverage_name + "\","
        output += '"' + self.access_count_key + '"' + ":" + str(self.access_count)
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The coverage_name is taken from the current object.
        The access counts are summed.
        :param <HACoverageInfo> another: an object to be merged with the current one.
        :return: <HASCoverageInfo>: the merged object.
        """
        ret = HAUsedCoveragesInfo(self.date, self.coverage_name, self.access_count + another.access_count)
        return ret

    """
    Keys for exporting to json.
    """
    date_key = "date"
    coverage_name_key = "id"
    access_count_key = "accessCount"
    # indicates the key after which the merging is done
    coverage_name_property_key = "coverage_name"
