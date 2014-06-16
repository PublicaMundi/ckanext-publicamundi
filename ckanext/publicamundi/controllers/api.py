import logging
import json
import time
import datetime

from pylons import g
from pylons.i18n import _

from ckan.lib.base import (BaseController, c, request, response, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi
import ckanext.publicamundi.lib.actions as publicamundi_actions

log1 = logging.getLogger(__name__)

content_types = {
    'json': 'application/json; charset=utf8',
}

class Controller(BaseController):

    def mimetype_autocomplete(self):
        q = request.params.get('incomplete', '')
        limit  = request.params.get('limit', 10)

        context = { 'model': model, 'session': model.Session }
        data_dict = { 'q': q, 'limit': limit }

        r = logic.get_action('mimetype_autocomplete')(context, data_dict)

        result_set = {
            'ResultSet': {
                'Result': [{'name': t } for t in r]
            }
        }

        response.headers['Content-Type'] = content_types['json']
        return [json.dumps(result_set)]


