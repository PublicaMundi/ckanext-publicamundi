from abc import abstractmethod
import urllib
import re
import datetime
#from os import listdir, extsep
import os

from pylons import config


class HAParser:
    """
    Adds functionality for parsing the HAProxy logs and gathering information about the services and coverage/layer bounding
    boxes access through the proxy. After being parsed the information in exported for other applications to use it.

    This class serves as base class for the specialized parsers.
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def __init__(self):
        """
        Class constructor.
        """
        logs_file_dir = config.get('ckanext.publicamundi.analytics.cache_dir')
        allowed_extensions = config.get('ckanext.publicamundi.analytics.allowed_extensions')

        log_files = []
        for filename in os.listdir(logs_file_dir):
            name, extension = filename.split(os.extsep, 1)
            if extension in allowed_extensions:
                log_files.append(os.path.join(logs_file_dir,filename))
        self.log_files = log_files

    @staticmethod
    def parse_date(line=""):
        """
        Parses the date from one line of log.
        :param <string> line: the line to be parsed.
        :return: <datetime> object representing the parsed date.
        """
        # split after spaces
        lines = line.split(" ")
        # first is month, second is day, add current year
        date_string = lines[0] + lines[1] + str(datetime.datetime.now().year)
        date = datetime.datetime.strptime(date_string, config.get('ckanext.publicamundi.analytics.ha_proxy_date_format'))
        return date

    @staticmethod
    def validate_line(line=""):
        """
        Validates a line of log, by removing multiple spaces, lower-casing it, checking if the line is non-empty and url unquoting.
        :param <string> line: the line to be validated.
        :return: <string> line with multiple spaces removed if line is valid, empty string otherwise.
        """
        ret = ""
        # only consider non-empty lines. They have at least 5 characters: month(3) and day(1) + space between them
        if len(line) > 4:
            # remove multiple spaces
            ret = re.sub(' +', ' ', line)
        return urllib.unquote(ret).lower()

    @staticmethod
    def merge_info_list(services_info_list, unique_key="date"):
        """
        Merges the current list of HA*Info objects by the given key. Objects having the same value for the given unique_key
        create a new object having the access counts added.
        :param: <[HA*Info]>: the list of objects to be merged.
        :param: <string> unique_key: the key of the property by which the merging is done.
        :return: <[HA*Info]> a list of objects representing the total services access counts for each different date.
        """
        unique_entries = []
        ret = []
        # parse the different dates
        for i in services_info_list:
            if getattr(i, unique_key) not in unique_entries:
                unique_entries.append(getattr(i, unique_key))
        # go through all dates and, for each unique date merge all the service info objects
        for i in unique_entries:
            partial_result = None
            for j in services_info_list:
                if i == getattr(j, unique_key):
                    # initialize partial_result if it is not initialized
                    if partial_result is None:
                        partial_result = j
                    else:
                        partial_result = partial_result.merge(j)
            ret.append(partial_result)
        return ret

    @abstractmethod
    def parse(self):
        """
        Classes which extend this one must provide this method which parses the current log file and return the
        targeted information.
        :return: <[HA*Info]>: a list of specialized objects describing the parsed information.
        """
        pass

    @staticmethod
    def print_as_json_array(object_list):
        """
        Returns a string representing the list of objects as a json array. Assumes that the objects implement 
        the __str__ method so they are already printed in json format.
        :param <[object]> the list of objects to be printed.
        :return: <string> the list as a json string.
        """
        # if the list is empty, print empty array
        if not object_list:
            return "[]"
        else:
            out = "["
            for i in object_list[:-1]:
                out += str(i)
                # add separator as this is not the last element
                out += ","
            # add last element
            out += str(object_list[-1])
            out += "]"
            return out


