import glob
import logging
from datetime import datetime, date, timedelta
from ckanext.publicamundi.analytics.controllers import configmanager
from ckanext.publicamundi.analytics.controllers.util import util

log1 = logging.getLogger(__name__)

class LogTrimmer:
    def __init__(self, log_pattern, exact_date):
        """
        Trims the log and saves only the lines on a specific date
        :param str log_pattern: the path pattern to the log files
        :param datetime exact_date: the date to restrict to
        """
        self.log_pattern = log_pattern
        self.exact_date = exact_date
        self.max_date = None

    def trim(self):
        """
        Returns the list of lines on the specified date
        :rtype: list[str]
        """
        logpaths = glob.glob(configmanager.logfile_pattern)
        line_list = []
        for logpath in logpaths:
            log1.info('Scanning logfile: %s', logpath)
            with file(logpath) as f:
                for line in f.readlines():
                    if self.line_has_correct_date(line, self.exact_date):
                        line_list.append(line)
        return line_list

    def get_max_date(self):
        return self.max_date + timedelta(seconds=1)

    def check_max_date(self, new_date):
        if self.max_date is None:
            self.max_date = new_date
        else:
            if self.max_date < new_date:
                self.max_date = new_date

    def line_has_correct_date(self, line, exact_date):
        try:
            line_date = util.parse_ha_date_from_line(line)
            self.check_max_date(line_date.date())
            if exact_date == line_date.date():
                return True
        except:
            # some wrongly formatted line, just skip it
            return False
