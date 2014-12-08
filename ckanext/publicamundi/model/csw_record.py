from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Table, Column, Integer, String, Text, DateTime,
    MetaData, ForeignKey, UniqueConstraint, Index)
from sqlalchemy.orm import relation, relationship, backref
from geoalchemy import Geometry, GeometryColumn, GeometryDDL, Polygon, Point

from ckan.model import Package

from ckanext.publicamundi.model import Base

class CswRecord(Base):
    __tablename__ = 'csw_record'

    # core; nothing happens without these
    identifier = Column('identifier', Text, ForeignKey(Package.id, ondelete='cascade'), primary_key=True)
    typename = Column('typename', Text, default='csw:Record', nullable=False, index=True)
    schema = Column('schema', Text, default='http://www.opengis.net/cat/csw/2.0.2', nullable=False, index=True)
    mdsource = Column('mdsource', Text, default='local', nullable=False, index=True)
    insert_date = Column('insert_date', Text, nullable=False, index=True)
    xml = Column('xml', Text, nullable=False)
    anytext = Column('anytext', Text, nullable=False)
    language = Column('language', Text, index=True)

    # identification
    type = Column('type', Text, index=True)
    title = Column('title', Text, index=True)
    title_alternate = Column('title_alternate', Text, index=True)
    abstract = Column('abstract', Text, index=True)
    keywords = Column('keywords', Text, index=True)
    keywordstype = Column('keywordstype', Text, index=True)
    parentidentifier = Column('parentidentifier', Text, index=True)
    relation = Column('relation', Text, index=True)
    time_begin = Column('time_begin', Text, index=True)
    time_end = Column('time_end', Text, index=True)
    topicategory = Column('topicategory', Text, index=True)
    resourcelanguage = Column('resourcelanguage', Text, index=True)

    # attribution
    creator = Column('creator', Text, index=True)
    publisher = Column('publisher', Text, index=True)
    contributor = Column('contributor', Text, index=True)
    organization = Column('organization', Text, index=True)

    # security
    securityconstraints = Column('securityconstraints', Text, index=True)
    accessconstraints = Column('accessconstraints', Text, index=True)
    otherconstraints = Column('otherconstraints', Text, index=True)

    # date
    date = Column('date', Text, index=True)
    date_revision = Column('date_revision', Text, index=True)
    date_creation = Column('date_creation', Text, index=True)
    date_publication = Column('date_publication', Text, index=True)
    date_modified = Column('date_modified', Text, index=True)

    format = Column('format', Text, index=True)
    source = Column('source', Text, index=True)

    # geospatial
    crs = Column('crs', Text, index=True)
    geodescode = Column('geodescode', Text, index=True)
    denominator = Column('denominator', Text, index=True)
    distancevalue = Column('distancevalue', Text, index=True)
    distanceuom = Column('distanceuom', Text, index=True)
    wkt_geometry = Column('wkt_geometry', Text)

    # service
    servicetype = Column('servicetype', Text, index=True)
    servicetypeversion = Column('servicetypeversion', Text, index=True)
    operation = Column('operation', Text, index=True)
    couplingtype = Column('couplingtype', Text, index=True)
    operateson = Column('operateson', Text, index=True)
    operatesonidentifier = Column('operatesonidentifier', Text, index=True)
    operatesoname = Column('operatesoname', Text, index=True)

    # additional
    degree = Column('degree', Text, index=True)
    classification = Column('classification', Text, index=True)
    conditionapplyingtoaccessanduse = Column('conditionapplyingtoaccessanduse', Text, index=True)
    lineage = Column('lineage', Text, index=True)
    responsiblepartyrole = Column('responsiblepartyrole', Text, index=True)
    specificationtitle = Column('specificationtitle', Text, index=True)
    specificationdate = Column('specificationdate', Text, index=True)
    specificationdatetype = Column('specificationdatetype', Text, index=True)

    # distribution
    # links: format "name,description,protocol,url[^,,,[^,,,]]"
    links = Column('links', Text, index=True)

    #geom = GeometryColumn('geom', Geometry(2), nullable=True)

    # def __init__(self, id, name, created_at=None):
    #     self.id = id
    #     self.name = name
    #     self.created_at = created_at or datetime.now();

def post_setup(engine):
    table_name = CswRecord.__tablename__
    table_language = 'english'
    postgis_geometry_column='wkb_geometry'
    conn = engine.connect()

    # Creating PostgreSQL Free Text Search (FTS) GIN index
    tsvector_fts = "ALTER TABLE %s add column anytext_tsvector tsvector" % table_name
    conn.execute(tsvector_fts)
    index_fts = "CREATE INDEX fts_gin_idx on %s using gin(anytext_tsvector)" % table_name
    conn.execute(index_fts)
    trigger_fts = "CREATE TRIGGER ftsupdate before insert or update on %s " \
       "for each row execute procedure tsvector_update_trigger" \
       " ('anytext_tsvector', 'pg_catalog.%s', 'anytext')" % (table_name, table_language)
    conn.execute(trigger_fts)

    #create_column_sql = "ALTER TABLE %s ADD COLUMN %s geometry(Geometry,4326);" % (table_name, postgis_geometry_column)
    create_column_sql = "SELECT AddGeometryColumn('public', '%s', '%s', 4326, 'POLYGON', 2)" % (table_name, postgis_geometry_column)
    
    create_insert_update_trigger_sql = '''
DROP TRIGGER IF EXISTS %(table)s_update_geometry ON %(table)s;
DROP FUNCTION IF EXISTS %(table)s_update_geometry();
CREATE FUNCTION %(table)s_update_geometry() RETURNS trigger AS $%(table)s_update_geometry$
BEGIN
    IF NEW.wkt_geometry IS NULL THEN
        RETURN NEW;
    END IF;
    NEW.%(geometry)s := ST_GeomFromText(NEW.wkt_geometry,4326);
    RETURN NEW;
END;
$%(table)s_update_geometry$ LANGUAGE plpgsql;

CREATE TRIGGER %(table)s_update_geometry BEFORE INSERT OR UPDATE ON %(table)s
FOR EACH ROW EXECUTE PROCEDURE %(table)s_update_geometry();
''' % {'table': table_name, 'geometry': postgis_geometry_column}

    create_spatial_index_sql = 'CREATE INDEX %(geometry)s_idx ON %(table)s USING GIST (%(geometry)s);' \
    % {'table': table_name, 'geometry': postgis_geometry_column}

    conn.execute(create_column_sql)
    conn.execute(create_insert_update_trigger_sql)
    conn.execute(create_spatial_index_sql)
    conn.close()

def pre_cleanup(engine):
    pass

# Note: needed to generate proper AddGeometryColumn statements
#GeometryDDL(CswRecord.__table__)

