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
from ckanext.publicamundi.lib.util import to_json
from ckanext.publicamundi.lib.metadata.vocabularies import vocabularies 

log1 = logging.getLogger(__name__)

content_types = {
    'json': 'application/json; charset=utf8',
}

class Controller(BaseController):

    # Autocomplete helpers
    
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
        return [to_json(result_set)]

    # Vocabularies

    # Note: The 1st thought was to rely on CKAN's vocabulary/tag functionality.
    # But because (e.g. for INSPIRE-related thesauri) we need to distinguish 
    # between the human and the machine-friendly view of a term, we had to use
    # our own vocabularies. So, provided that we had some way to solve this,
    # the following api calls should not be needed any more.

    def vocabularies_list(self):
        response.headers['Content-Type'] = content_types['json']
        return [json.dumps(vocabularies.keys())]

    def vocabulary_get(self, name):
        name = str(name)
        r = None
        
        if name in vocabularies:
            vocab = vocabularies[name]
            terms = vocab['vocabulary'].by_value
            r = {
                'date_type': vocab.get('date_type'),
                'reference_date': vocab.get('reference_date'),
                'title': vocab.get('title'),
                'name': vocab.get('name'),
                'terms': [{ 'value': k, 'title': terms[k].title } for k in terms],
            }
                
        response.headers['Content-Type'] = content_types['json']
        return [to_json(r)]


