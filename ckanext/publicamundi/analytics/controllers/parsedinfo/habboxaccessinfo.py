from sqlalchemy import Column, Integer, Date, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from ckanext.publicamundi.analytics.controllers.configmanager import Base
from ckanext.publicamundi.analytics.controllers.util.habbox import HABbox


class HABboxAccessInfo(Base):
    """
    Keeps information about all accessed bounding boxes.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"
    __tablename__ = "bbox_access"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    bbox_id = Column(Integer, ForeignKey("bbox.id"), nullable=False)
    bbox = relationship("HABbox",
                        backref=backref("bbox_access", uselist=False))
    access_count = Column(Integer, nullable=False)
    crs = Column(String, nullable=False)

    def __init__(self, date, bbox, access_count=0, crs=""):
        """
        CLass constructor.
        :param HABbox bbox: the bbox corresponding to this entry.
        :param <int> access_count: how many times this bbox has been accessed.
        :param <string> crs: the crs in which this bbox is defined.
        """
        self.bbox = bbox
        self.access_count = access_count
        self.crs = crs
        self.date = date

    def __str__(self):
        """
        Override of __str__.
        Handles the way the object is printed. The current format is json.
        """
        output = "{"
        output += '"' + self.bbox_key + '"' + ":" + self.bbox.to_coordinates_str() + ","
        output += '"' + self.access_count_key + '"' + ":" + str(self.access_count) + ","
        output += '"' + self.crs_key + '"' + ":\"" + self.crs + "\""
        output += "}"
        return output

    def merge(self, another):
        """
        Merges 2 objects. The bbox and crs are taken from the current object.
        The access counts are summed.
        :param <HABboxAccessInfo> another: an object to be merged with the current one.
        :return: <HABboxAccessInfo>: the merged object.
        """
        ret = HABboxAccessInfo(
            self.date, 
            HABbox(
                self.bbox.min_x, self.bbox.min_y, self.bbox.max_x, self.bbox.max_y),
            self.access_count + another.access_count, self.crs)
        return ret

    """
    Keys for exporting to json.
    """
    bbox_key = "bbox"
    access_count_key = "accessCount"
    crs_key = "crs"
    # the key of the property on which the merge is done
    bbox_property_key = "bbox"
