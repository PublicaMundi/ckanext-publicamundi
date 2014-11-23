from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Table, Column, Integer, String, DateTime, 
    MetaData, ForeignKey, UniqueConstraint, Index)
from sqlalchemy.orm import relation, relationship, backref
from geoalchemy import Geometry, GeometryColumn, GeometryDDL, Polygon, Point

from ckan.model import Package

from ckanext.publicamundi.model import Base

class CswRecord(Base):
    __tablename__ = 'csw_record'

    id = Column('id', String(64), ForeignKey(Package.id, ondelete='cascade'), primary_key=True)
    title = Column('title', String(256), nullable=True)
    name = Column('name', String(64), nullable=False, index=True)
    created_at = Column('created_at', DateTime(), nullable=False)
    geom = GeometryColumn('geom', Geometry(2), nullable=True)

    uniq_name = UniqueConstraint('name')

    def __init__(self, id, name, created_at=None):
        self.id = id
        self.name = name
        self.created_at = created_at or datetime.now();

    def __unicode__(self):
        return "<CswRecord \"%s\">" % (self.name)

# Note: needed to generate proper AddGeometryColumn statements
GeometryDDL(CswRecord.__table__)

