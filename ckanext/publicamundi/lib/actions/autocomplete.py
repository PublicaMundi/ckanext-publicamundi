import logging
import json
import time
import datetime

from pylons import g, config

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

_ = toolkit._
_get_action = toolkit.get_action
_check_access = toolkit.check_access

@logic.side_effect_free
def mimetype_autocomplete(context, data_dict):
    '''Return a list of MIME types whose names contain a string.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of resource formats to return (optional,default: 5)
    :type limit: int

    :rtype: list of strings
    '''

    _check_access('site_read', context, data_dict)

    q = data_dict.get('q', None)
    if not q:
        return []

    limit = int(data_dict.get('limit', 5))

    mime_types = toolkit.aslist(
        config.get('ckanext.publicamundi.mime_types', ''))
    results = []
    n = 0
    for t in mime_types:
        if t.find(q) >= 0:
            results.append(t)
            n += 1
            if n == limit:
                break

    return results

