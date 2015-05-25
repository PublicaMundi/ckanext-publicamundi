from ckan.lib.base import (redirect, BaseController, render)

import pylons.config as config
from ckan.lib import helpers
import ckan.plugins.toolkit as toolkit

class Controller(BaseController):
    def developers(self):
        return render('developers/index.html')

