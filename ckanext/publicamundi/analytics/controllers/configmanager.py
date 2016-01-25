import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()

# The following module globals will be initialized when configuration is available

database_url = None
database_engine = None
session = None
Session = None

export_date_format = '%Y-%m-%d'
ha_proxy_time_format = '%d/%b/%Y:%H:%M:%S'
logfile_pattern = None

def setup(config):
    '''Setup this module when configuration is available.
    '''

    global database_url
    global database_engine
    global Session
    global session

    global export_date_format
    global ha_proxy_datetime_format
    global logfile_pattern

    # Database-related options, session factory

    database_url = config.get(
        'ckanext.publicamundi.analytics.database_url',
        'postgresql://pman:pass@localhost/analytics')

    database_engine = create_engine(database_url)
    
    Base.metadata.bind = database_engine
   
    Session = scoped_session(sessionmaker(bind=database_engine))
    session = Session()
    
    # Parse-related options

    logfile_pattern = config.get(
        'ckanext.publicamundi.analytics.logfile_pattern',
        '/mnt/hgfs/logs/*.log')

    export_date_format = config.get(
        'ckanext.publicamundi.analytics.export_date_format',
        '%Y-%m-%d')

    ha_proxy_datetime_format = config.get(
        'ckanext.publicamundi.analytics.ha_proxy_datetime_format',
        '%d/%b/%Y:%H:%M:%S')

    
