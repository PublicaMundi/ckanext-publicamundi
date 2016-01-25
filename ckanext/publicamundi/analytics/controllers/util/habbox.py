"""
Class representing a 2D bounding box, as it appears in the HAProxy logs.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from ckanext.publicamundi.analytics.controllers.configmanager import Base

__author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"


class HABbox(Base):
    __tablename__ = "bbox"

    id = Column(Integer, primary_key=True)
    #bbox_access_id = Column(Integer, ForeignKey("bbox_access.id"))
    min_x = Column(String, nullable=False)
    min_y = Column(String, nullable=False)
    max_x = Column(String, nullable=False)
    max_y = Column(String, nullable=False)

    def __init__(self, min_x, min_y, max_x, max_y):
        """
        Class constructor.
        @:param <string or int> min_x: minimum on the first axis.
        @:param <string or int> min_y: minimum on the second axis.
        @:param <string or int> max_x: maximum on the first axis.
        @:param <string or int> max_y: maximum on the second axis.
        """
        self.min_x = str(min_x)
        self.min_y = str(min_y)
        self.max_x = str(max_x)
        self.max_y = str(max_y)

    def to_coordinates_str(self):
        """
        Converts the object in a string representing an array of coordinates, as expected by OpenLayers.
        :return: <string> representation as coordinates.
        """
        # check if all the points are specified
        if not self.min_x or not self.min_y or not self.max_x or not self.max_y:
            return ""
        output = "[["
        # lower left
        output += "[" + self.min_x + "," + self.min_y + "]" + ","
        # upper left
        output += "[" + self.min_x + "," + self.max_y + "]" + ","
        # upper right
        output += "[" + self.max_x + "," + self.max_y + "]" + ","
        # lower right
        output += "[" + self.max_x + "," + self.min_y + "]"
        output += "]]"
        return output

    def __eq__(self, other):
        """
        Overriding equality by value to mean that all coordinates are equal respectively.
        :param <HABbox> other: the object to be compared to.
        :return: <boolean> true if the coordinates are equal accordingly in the 2 objects.
        """
        return self.min_x == other.min_x and self.min_y == other.min_y and \
            self.max_x == other.max_x and self.max_y == other.max_y