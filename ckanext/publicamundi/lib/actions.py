import logging
import json
import time
import datetime
import requests
import urlparse

from beaker.cache import (cache_regions, cache_region)
from pylons import g, config
from pylons.i18n import _

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckanext.publicamundi.lib.metadata import (
    dataset_types, make_object, serializer_for, xml_serializer_for)

log1 = logging.getLogger(__name__)

_ = toolkit._

url_for = toolkit.url_for
get_action = toolkit.get_action

@logic.side_effect_free
def mimetype_autocomplete(context, data_dict):
    '''Return a list of MIME types whose names contain a string.

    :param q: the string to search for
    :type q: string
    :param limit: the maximum number of resource formats to return (optional,default: 5)
    :type limit: int

    :rtype: list of strings
    '''

    model, session = context['model'], context['session']

    toolkit.check_access('site_read', context, data_dict)

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

def package_import(context, data_dict):
    '''Import a dataset from a given source.

    :param source: a (local or external) URL where metadata is located
    :type q: string
    
    :param dtype: the dataset-type i.e. the schema of imported metadata
    :type dtype: string
    
    :param on_errors: hint on what to do when validation errors are encountered
    :type on_errors: enum {'continue', 'abort'}
    
    :param on_name_conflict: hint on what to do when a name conflict is encountered
    :type on_name_conflict: enum {'rename', 'abort'}

    :rtype: A status message 
    '''

    result = { 'message': None }
   
    model, session = context['model'], context['session']
     
    toolkit.check_access('package_create', context, data_dict)
    
    # Read params

    source = data_dict.get('source')
    if not source.startswith('http://'):
        source = config['ckan.site_url'] + source.strip('/')
    source = urlparse.urlparse(source)

    dtype = data_dict.get('dtype', 'ckan')
    on_errors = data_dict.get('on_errors', 'abort')
    on_name_conflict = data_dict.get('on_name_conflict', 'abort')

    # Fetch raw XML data

    xmldata = None
    r = requests.get(source.geturl())
    if not r.ok:
        raise ValueError('Cannot fetch metadata from source URL')
    elif not r.headers['content-type'] in ['application/xml', 'text/xml']:
        raise ValueError('The given source does not contain XML data')
    else:
        xmldata = r.content

    # Parse XML data as metadata of `dtype` schema
    
    obj = make_object(dtype)
    try:
        obj = xml_serializer_for(obj).loads(xmldata)
    except:
        # Map all parse exceptions to Invalid (even assertions)
        raise toolkit.Invalid('The given XML file is malformed')

    # Prepare package dict
    
    pkg_dict = obj.deduce_basic_fields()
    pkg_dict.update({ 
        'dataset_type': dtype,
        dtype: obj.to_dict(flat=False),
    })
    
    # Check name is available
    # Note: We just find the 1st available name, of course this doesnt guarantee that 
    # it will remain available at the actual time `package_create` is called.
    
    name, name_found = pkg_dict['name'], False
    while False and not name_found:
        try:
            get_action('package_show')(context, data_dict=dict(id=name))
        except toolkit.ObjectNotFound:
            name_found = True
        else:
            if on_name_conflict == 'abort':
                raise ValueError('The package name %r is not available' % (name))
            else:
                # Todo Rename and retry
                name = name + '~1' 
   
    # Workaround for https://github.com/ckan/ckanext-harvest/issues/84
    # context.pop('__auth_audit', None)
    
    # Create/Update package
     
    #pkg_dict['state'] = 'invalid'
    try:
        x = get_action('package_create')(context, data_dict=pkg_dict)
    except toolkit.ValidationError as ex:
        if 'name' in ex.error_dict:
            # The name is taken
            assert False, 'name taken'
        else:
            # The dataset is invalid
            #assert False, 'validation failed'
            log1.warn(' ** Validation failed for %r ' % (name))
            context['skip_validation'] = True
            pkg_dict['state'] = 'invalid'
            x = get_action('package_create')(context, data_dict=pkg_dict)

    
    result['name'] = x['name'] 
    result['state'] = x.get('state')
    
    #assert False
    return result


