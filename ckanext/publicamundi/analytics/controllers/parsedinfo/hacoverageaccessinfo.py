from pylons import config

class HACoverageAccessInfo:
    """
    Stores information about coverages and layers in the HA log:
     - the date of the entry
     - coverage/layer name
     - access count
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self, date, access_count=0):
        """
        Class constructor.
        :param <datetime> date: the date of the current entry.
        :param <int> access_count: the access count for the entry.
        """
        self.date = date
        self.access_count = access_count

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += self.date_key + ":\"" + self.date.strftime(config.get('ckanext.publicamundi.analytics.export_date_format')) + "\","
        output += self.access_count_key + ":" + str(self.access_count)
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The date of the resulting object is the date of the current one.
        The access counts are summed.
        :param <HACoverageInfo> another: an object to be merged with the current one.
        :return: <HASCoverageInfo>: the merged object.
        """
        # if another is a list merge with every element
        ret = HACoverageAccessInfo(self.date)
        ret.access_count = self.access_count + another.access_count
        return ret

    """
    Keys for exporting to json.
    """
    date_key = "date"
    access_count_key = "accessCount"
