import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .csw_record import CswRecord

from .resource_ingest import ResourceIngest
