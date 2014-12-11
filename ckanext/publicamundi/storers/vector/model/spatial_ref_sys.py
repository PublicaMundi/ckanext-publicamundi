from sqlalchemy import Table, Column, String, Integer

from ckan.model import Session

import celery as _celery
from ckan.lib.celery_app import celery

from ckanext.publicamundi.model import Base
import ckanext.publicamundi.storers.vector as vectorstorer


class SpatialRefSys(Base):
    __tablename__ = 'spatial_ref_sys'
    srid = Column('srid', Integer, primary_key=True)
    auth_name = Column('auth_name', String(256))
    auth_srid = Column('auth_srid', Integer)
    srtext = Column('srtext', String(2048))
    proj4text = Column('proj4text', String(2048))

    def __init__(
            self,
            srid,
            auth_name,
            auth_srid,
            srtext,
            proj4text):

        self.srid = srid
        self.auth_name = auth_name
        self.auth_srid = auth_srid
        self.srtext = srtext
        self.proj4text = proj4text

    def get_proj4_text(self):
        return self.proj4text

    def get_autocomplete_dict(self):
        autocomplete_dict = {}
        spatial_ref = vectorstorer.osr.SpatialReference()
        spatial_ref.ImportFromEPSG(self.srid)
        srs_wkt = spatial_ref.ExportToWkt()
        geogcs = spatial_ref.GetAttrValue("GEOGCS", 0)
        autocomplete_dict['label'] = geogcs + " - " + str(self.srid)
        autocomplete_dict['value'] = self.srid
        return autocomplete_dict
