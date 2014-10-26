import logging
import json
import time
import datetime

from beaker.cache import (cache_regions, cache_region)
from pylons import g
from pylons.i18n import _

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi

log1 = logging.getLogger(__name__)

# Some common MIME types
mime_types = [
    'text/plain', 
    'text/html', 
    'text/xml', 
    'text/xhtml', 
    'text/svg', 
    'text/csv', 
    'text/json', 
    'text/javascript',
    'application/zip', 
    'application/x-gzip', 
    'application/x-tar', 
    'application/x-bzip2', 
    'application/json',
    'application/vnd.ms-excel', 
    'application/ms-word', 
    'application/vnd.ms-powerpoint',
    'application/pdf',
    'application/octet-stream', 
    'image/x-dwg', 
    'application/dwg', 
    'application/x-dwg', 
    'application/x-autocad', 
    'image/vnd.dwg', 
    'drawing/dwg',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.oasis.opendocument.presentation', 
    'application/vnd.oasis.opendocument.spreadsheet',
    'image/png',
    'image/jpeg',
    'image/bmp',
    'image/tiff',
    'image/gif',
    'video/avi',
    'video/mpeg',
    'audio/mpeg',
    'audio/vorbis',
];

@logic.side_effect_free
def mimetype_autocomplete(context, data_dict):
    '''Return a list of MIME types whose names contain a string.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of resource formats to return (optional,default: 5)
    :type limit: int

    :rtype: list of strings
    '''

    model   = context['model']
    session = context['session']

    toolkit.check_access('site_read', context, data_dict)

    q = data_dict.get('q', None)
    if not q:
        return []

    limit = int(data_dict.get('limit', 5))

    results = []
    n = 0
    for t in mime_types:
        if t.find(q) >= 0:
            results.append(t)
            n += 1
            if n == limit:
                break

    return results

