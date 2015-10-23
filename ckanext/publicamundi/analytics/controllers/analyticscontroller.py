from ckan.lib.base import BaseController
from ckan.lib.base import (
    BaseController, c, request, session, render, config, abort)
from ckanext.publicamundi.analytics.controllers.orchestrator.server_orchestrator import ServerOrchestrator
import pylons.config as global_config
from ckanext.publicamundi.analytics.controllers.orchestrator.tiling_orchestrator import TilingOrchestrator


class AnalyticsController(BaseController):
    """
    /analytics:
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def analytics(self):
        """
        """
        return render("main.html")

    def adjust_workers(self, number):
        so = self.get_service_orchestrator()
        so.adjust(number)

    def adjust_tiling(self):
        to = self.get_tiling_orchestrator()
        to.adjust()

    def adjust_cache(self, wcs, wms):
        so = self.get_service_orchestrator()
        so.adjust_cache(wcs, wms)

    def adjust_pyramids(self, layer):
        to = self.get_tiling_orchestrator()
        to.adjust_pyramids(layer)

    def get_service_orchestrator(self):
        so = ServerOrchestrator(global_config.get("ckanext.publicamundi.analytics.api_endpoint", ""),
                                global_config.get("ckanext.publicamundi.analytics.rasdaman_endpoint", ""))
        return so

    def get_tiling_orchestrator(self):
        to = TilingOrchestrator(global_config.get("ckanext.publicamundi.analytics.api_endpoint", ""),
                                global_config.get("ckanext.publicamundi.analytics.rasdaman_endpoint", ""))
        return to

