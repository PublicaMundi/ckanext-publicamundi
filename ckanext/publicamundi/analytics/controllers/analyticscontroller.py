from ckan.lib.base import BaseController
from ckan.lib.base import(
    BaseController, c, request, session, render, config, abort)
import ckan.new_authz as new_authz

class AnalyticsController(BaseController):
    """
    /analytics:
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def analytics(self):
        c.is_sysadmin = new_authz.is_sysadmin(c.user)
        return render("main.html")
