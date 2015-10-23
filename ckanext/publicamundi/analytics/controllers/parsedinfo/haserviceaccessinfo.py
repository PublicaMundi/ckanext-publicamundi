from ckanext.publicamundi.analytics.controllers.configmanager import ConfigManager


class HAServiceAccessInfo:
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

    def __init__(self, date, rasdaman=0, rasdaman_wcs=0, rasdaman_wcps=0, rasdaman_wms=0, geoserver=0):
        """
        Class constructor.
        :param <datetime> date: the date of the entry.
        :param <int> rasdaman: the number of rasdaman service accesses.
        :param <int> rasdaman_wcs: the number of rasdaman_wcs service accesses.
        :param <int> rasdaman_wcps: the number of rasdaman_wcps service accesses.
        :param <int> rasdaman_wms: the number of rasdaman_wms service accesses.
        :param <int> geoserver: the number of geoserver service accesses.
        """
        self.rasdaman_wms = rasdaman_wms
        self.rasdaman_wcps = rasdaman_wcps
        self.rasdaman_wcs = rasdaman_wcs
        self.rasdaman = rasdaman
        self.geoserver = geoserver
        self.date = date

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += '"' + self.date_key + '"' + ":\"" + self.date.strftime(ConfigManager.export_date_format) + "\","
        output += '"' + self.rasdaman_key + '"' + ":" + str(self.rasdaman) + ","
        output += '"' + self.rasdaman_wcs_key + '"' + ":" + str(self.rasdaman_wcs) + ","
        output += '"' + self.rasdaman_wcps_key + '"' + ":" + str(self.rasdaman_wcps) + ","
        output += '"' + self.rasdaman_wms_key + '"' + ":" + str(self.rasdaman_wms) + ","
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
        ret.rasdaman_wcs = self.rasdaman_wcs + another.rasdaman_wcs
        ret.rasdaman_wcps = self.rasdaman_wcps + another.rasdaman_wcps
        ret.rasdaman_wms = self.rasdaman_wms + another.rasdaman_wms
        ret.geoserver = self.geoserver + another.geoserver
        return ret

    """
    Keys for exporting to json.
    """
    date_key = "date"
    rasdaman_key = "rasdaman"
    rasdaman_wcs_key = "rasdaman_wcs"
    rasdaman_wcps_key = "rasdaman_wcps"
    rasdaman_wms_key = "rasdaman_wms"
    geoserver_key = "geoserver"
