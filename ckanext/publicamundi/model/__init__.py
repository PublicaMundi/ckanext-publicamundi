from datetime import datetime;

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relation, relationship, backref

Base = declarative_base()

class CswRecord(Base):
    __table__ = Table ('csw_record', Base.metadata,
        Column('id', Integer(), primary_key=True),
        Column('title', String(256), nullable=True),
        Column('name', String(64), nullable=False, index=True),
        Column('created_at', DateTime(), nullable=False),
        UniqueConstraint('name'),
    )

    def __init__(self, name):
        self.name  = name
        self.created_at = created_at or datetime.now();

    def __unicode__(self):
        return "<CswRecord \"%s\">" % (self.name)


