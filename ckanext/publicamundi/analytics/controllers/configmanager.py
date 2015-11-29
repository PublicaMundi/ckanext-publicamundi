import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pylons.config as global_config


class ConfigManager:
    """
    Stores config information used by the application.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self):
        pass

    # the format in which the date is exported
    export_date_format = global_config.get("ckanext.publicamundi.analytics.export_date_format", "%Y-%m-%d")
    ha_proxy_time_format = global_config.get("ckanext.publicamundi.analytics.ha_proxy_datetime_format",
                                             "%d/%b/%Y:%H:%M:%S")

    # path to the log file
    log_file_patterns = global_config.get("ckanext.publicamundi.analytics.log_pattern", "/mnt/hgfs/logs/*.log")

    # database connection
    database_connection_string = global_config.get("ckanext.publicamundi.analytics.database_conn_url", "postgresql://pman:pass@localhost/analyticsdb")


Base = declarative_base()
database_engine = create_engine(ConfigManager.database_connection_string)
Base.metadata.bind = database_engine
DBSession = sessionmaker(bind=database_engine)
session = DBSession()