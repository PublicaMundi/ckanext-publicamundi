import logging
import json

from pylons import url

from ckan.lib.base import (BaseController, c, request, response, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi

log1 = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self, id=None):
        #return toolkit.render('', data)
        return 'Another test!!'

