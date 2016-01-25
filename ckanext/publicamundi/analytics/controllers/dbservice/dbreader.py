from ckanext.publicamundi.analytics.controllers import configmanager
from ckanext.publicamundi.analytics.controllers.parsedinfo.habboxaccessinfo import HABboxAccessInfo
from ckanext.publicamundi.analytics.controllers.parsedinfo.hacoveragebandsinfo import HACoverageBandsInfo
from ckanext.publicamundi.analytics.controllers.parsedinfo.haserviceaccessinfo import HAServiceAccessInfo
from ckanext.publicamundi.analytics.controllers.parsedinfo.hausedcoveragesinfo import HAUsedCoveragesInfo
from ckanext.publicamundi.analytics.controllers.parsers.haparser import HAParser
from ckanext.publicamundi.analytics.controllers.util.system import SystemInfo


class DbReader:
    def __init__(self):
        pass

    @staticmethod
    def read_used_coverages_totals(start_date, end_date):
        session = configmanager.session
        used_coverages = session.query(HAUsedCoveragesInfo).filter(
            HAUsedCoveragesInfo.date.between(start_date, end_date)).all()
        return HAParser.merge_info_list(
            used_coverages, HAUsedCoveragesInfo.coverage_name_property_key)

    @staticmethod
    def read_service_access_by_date(start_date, end_date):
        session = configmanager.session
        service_access = session.query(HAServiceAccessInfo).filter(
            HAServiceAccessInfo.date.between(start_date, end_date)).all()
        return HAParser.merge_info_list(service_access, HAServiceAccessInfo.date_key)

    @staticmethod
    def read_coverage_bands_totals(coverage_name, start_date, end_date):
        session = configmanager.session
        coverage_bands = session.query(HACoverageBandsInfo).filter(
            (HACoverageBandsInfo.date.between(start_date, end_date)) &
            (HACoverageBandsInfo.coverage_name == coverage_name)).all()
        return HAParser.merge_info_list(
            coverage_bands, HACoverageBandsInfo.band_property_key)

    @staticmethod
    def read_coverage_access_by_date(coverage_name, start_date, end_date):
        session = configmanager.session
        coverage_access = session.query(HAUsedCoveragesInfo).filter(
            (HAUsedCoveragesInfo.coverage_name == coverage_name) &
            (HAUsedCoveragesInfo.date.between(start_date, end_date))).all()
        return HAParser.merge_info_list(
            coverage_access, HAUsedCoveragesInfo.date_key)

    @staticmethod
    def read_bbox_access_totals(start_date, end_date):
        session = configmanager.session
        bbox_access = session.query(HABboxAccessInfo).filter(
            HABboxAccessInfo.date.between(start_date, end_date)).all()
        return HAParser.merge_info_list(bbox_access, HABboxAccessInfo.bbox_key)

    @staticmethod
    def read_system_info():
        session = configmanager.session
        system_info = session.query(SystemInfo).filter(
            SystemInfo.key == SystemInfo.LATEST_DATE_KEY).one()
        return system_info
