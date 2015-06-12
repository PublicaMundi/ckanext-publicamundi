import os
class ConfigManager:
    """
    Stores config information used by the application.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self):
        pass

    # the format in which the date is exported
    export_date_format = "%Y-%m-%d"
    ha_proxy_date_format = "%b%d%Y"

    # path to the log file
    log_file_path = os.path.dirname(os.path.realpath(__file__)) + "/example_log.txt"
