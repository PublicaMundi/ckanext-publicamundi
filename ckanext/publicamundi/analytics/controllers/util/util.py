from ckanext.publicamundi.analytics.controllers.configmanager import ConfigManager
from datetime import datetime


def parse_ha_date_from_line(line):
    parts = line.split(" ")
    line_date = datetime.strptime(parts[6].split(".")[0][1:], ConfigManager.ha_proxy_time_format)
    return line_date
