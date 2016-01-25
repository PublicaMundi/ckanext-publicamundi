from sqlalchemy import Column, Integer, Date
from ckanext.publicamundi.analytics.controllers import configmanager

Base = configmanager.Base

class HAServiceAccessInfo(Base):
    """
    Stores information about the HA log:
     - the date of the entry
     - rasdaman access count
     - rasdaman_wcs access count
     - rasdaman_wms access count
     - rasdaman_wcps access count
     - geoserver access count
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"
    __tablename__ = "service_access"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    wms = Column(Integer, nullable=False)
    wcps = Column(Integer, nullable=False)
    wcs = Column(Integer, nullable=False)
    rasdaman = Column(Integer, nullable=False)
    geoserver = Column(Integer, nullable=False)

    def __init__(self, date, rasdaman=0, wcs=0, wcps=0, wms=0, geoserver=0):
        """
        Class constructor.
        :param <datetime> date: the date of the entry.
        :param <int> rasdaman: the number of rasdaman service accesses.
        :param <int> wcs: the number of rasdaman_wcs service accesses.
        :param <int> wcps: the number of rasdaman_wcps service accesses.
        :param <int> wms: the number of rasdaman_wms service accesses.
        :param <int> geoserver: the number of geoserver service accesses.
        """
        self.wms = wms
        self.wcps = wcps
        self.wcs = wcs
        self.rasdaman = rasdaman
        self.geoserver = geoserver
        self.date = date

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += '"' + self.date_key + '"' + ":\"" +\
            self.date.strftime(configmanager.export_date_format) + "\","
        output += '"' + self.rasdaman_key + '"' + ":" + str(self.rasdaman) + ","
        output += '"' + self.wcs_key + '"' + ":" + str(self.wcs) + ","
        output += '"' + self.wcps_key + '"' + ":" + str(self.wcps) + ","
        output += '"' + self.wms_key + '"' + ":" + str(self.wms) + ","
        output += '"' + self.geoserver_key + '"' + ":" + str(self.geoserver)
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The date of the resulting object is the date of the current one.
        All other attributes are summed.
        :param <HAServiceInfo> another: an object to be merged with the current one.
        :return: <HAServiceInfo>: the merged object.
        """
        # if another is a list merge with every element
        ret = HAServiceAccessInfo(self.date)
        ret.rasdaman = self.rasdaman + another.rasdaman
        ret.wcs = self.wcs + another.wcs
        ret.wcps = self.wcps + another.wcps
        ret.wms = self.wms + another.wms
        ret.geoserver = self.geoserver + another.geoserver
        return ret

    """
    Keys for exporting to json.
    """
    date_key = "date"
    rasdaman_key = "rasdaman"
    wcs_key = "wcs"
    wcps_key = "wcps"
    wms_key = "wms"
    geoserver_key = "geoserver"
