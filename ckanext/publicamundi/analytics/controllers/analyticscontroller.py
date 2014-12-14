from ckan.lib.base import BaseController
from ckan.lib.base import(
    BaseController, c, request, session, render, config, abort)

class AnalyticsController(BaseController):
    """
    /analytics:
    """
    __author__ = "<a href='mailto:merticariu@rasdaman.com'>Vlad Merticariu</a>"

    def analytics(self):
        """
        """
	return render("main.html")
