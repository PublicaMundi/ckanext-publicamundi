import argparse
import sys
from sqlalchemy.orm.exc import NoResultFound
from ckanext.publicamundi.analytics.controllers.configmanager import ConfigManager, Base, session
from ckanext.publicamundi.analytics.controllers.dbservice.dbreader import DbReader
from ckanext.publicamundi.analytics.controllers.log_trimmer import LogTrimmer
from ckanext.publicamundi.analytics.controllers.parsers.habboxaccessparser import HABboxAccessParser
from ckanext.publicamundi.analytics.controllers.parsers.hacoveragebandparser import HACoverageBandParser
from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckanext.publicamundi.analytics.controllers.parsers.haservicesaccessparser import HAServicesAccessParser
from ckanext.publicamundi.analytics.controllers.dbservice.dbmanager import DbManager
from datetime import datetime, timedelta
from datetime import date
from dateutil.parser import parse
from ckanext.publicamundi.analytics.controllers.parsers.hausedcoveragesparser import HAUsedCoveragesParser
from ckanext.publicamundi.analytics.controllers.util.system import SystemInfo

argp = argparse.ArgumentParser()
argp.add_argument ("--debug", dest='debug', default=False, action='store_true');

def get_latest_parse_date():
    try:
        latest_date_str = DbReader.read_system_info().value
        return parse(latest_date_str)
    except:
        return date.fromordinal(date.today().toordinal() - 1)


def get_parse_dates():
    start_date, end_date = None, None
    if len(sys.argv) == 3:
        try:
            start_date = parse(sys.argv[1])
            end_date = parse(sys.argv[2])
        except:
            print "Could not parse the given date. Please input a starting and ending date in ISO format"
            exit(1)
    else:
        start_date = get_latest_parse_date()
        end_date = datetime.now()

    return start_date, end_date


def main(debug=False):
    
    if debug:
        DbManager.drop_all_tables()
    DbManager.create_schema()

    start_date, end_date = get_parse_dates()
    current_date = start_date.date()
    finish_date = end_date.date()
    while current_date < finish_date:
        print "Parsing from {0}".format(current_date)
        trimmer = LogTrimmer(ConfigManager.log_file_patterns, current_date)
        log_lines = trimmer.trim()
        update_latest_parse_date(current_date)
        parse_all(log_lines)
        current_date = current_date + timedelta(days=1)


def parse_all(log_lines):
    parsers = [HAUsedCoveragesParser, HAServicesAccessParser, HACoverageBandParser, HABboxAccessParser]
    for parser in parsers:
        persist_info_list(parser(log_lines).parse())


def persist_info_list(info_list):
    for info in info_list:
        session.add(info)
    session.commit()


def update_latest_parse_date(latest_date):
    info = None
    try:
        info = session.query(SystemInfo).filter(SystemInfo.key == SystemInfo.LATEST_DATE_KEY).one()
        info.value = str(latest_date)
    except NoResultFound:
        info = SystemInfo(SystemInfo.LATEST_DATE_KEY, str(latest_date))
    session.add(info)


if __name__ == "__main__":
    args = argp.parse_args()
    main(args.debug)
