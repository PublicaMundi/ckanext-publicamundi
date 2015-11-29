from ckan.lib.base import BaseController
from ckan.lib.base import (
    BaseController, c, request, session, render, config, abort)
import json
import ckan.new_authz as new_authz
from ckanext.publicamundi.analytics.controllers.orchestrator.server_orchestrator import ServerOrchestrator
import pylons.config as global_config
from ckanext.publicamundi.analytics.controllers.orchestrator.tiling_orchestrator import TilingOrchestrator


class AnalyticsController(BaseController):
    """
    /analytics:
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def analytics(self):
        c.is_sysadmin = new_authz.is_sysadmin(c.user)
        return render("main.html")

    def adjust_workers(self, number):
        so = self.get_service_orchestrator()
        if int(number) == 0:
            return str(so.get_new_number_of_servers())
        return str(so.adjust(number))

    def adjust_tiling(self, coverage_name):
        to = self.get_tiling_orchestrator()
        return str(to.retile_coverage(coverage_name))

    def describe_tiling(self, coverage_name):
        to = self.get_tiling_orchestrator()
        return str(to.adjust_description(coverage_name))

    def adjust_cache(self, wcs, wms):
        so = self.get_service_orchestrator()
        if int(wcs) == 0 or int(wms) == 0:
            result = json.dumps(so.get_cache())
        else:
            result = json.dumps(so.adjust_cache(wcs, wms))
        return str(result)

    def adjust_pyramids(self, layer, levels):
        to = self.get_tiling_orchestrator()
        return str(to.adjust_pyramids(layer, levels))

    def get_service_orchestrator(self):
        so = ServerOrchestrator(global_config.get("ckanext.publicamundi.analytics.api_endpoint", ""),
                                global_config.get("ckanext.publicamundi.analytics.rasdaman_endpoint", ""))
        return so

    def get_tiling_orchestrator(self):
        to = TilingOrchestrator(global_config.get("ckanext.publicamundi.analytics.api_endpoint", ""),
                                global_config.get("ckanext.publicamundi.analytics.rasdaman_endpoint", ""))
        return to

