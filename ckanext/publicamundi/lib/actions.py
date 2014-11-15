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
check_access = toolkit.check_access

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

@logic.side_effect_free
def package_export(context, data_dict):
    '''Export a dataset to XML.
    '''
    raise NotImplementedError('Todo')

def package_import(context, data_dict):
    '''Import a dataset from a given XML source.

    :param source: a (local or external) URL where metadata is located
    :type q: string
    
    :param dtype: the dataset-type i.e. the schema of imported metadata
    :type dtype: string

    :param owner_org: the machine-name for the owner organization 
    :type owner_org: string

    :param on_errors: hint on what to do when validation errors are encountered
    :type on_errors: enum {'continue', 'abort'}
    
    :param on_name_conflict: hint on what to do when a name conflict is encountered
    :type on_name_conflict: enum {'rename', 'abort'}

    :rtype: basic info for the newly created package 
    '''
      
    # Read parameters

    try:
        source = data_dict['source']
    except KeyError:
        raise ValueError('The `source` parameter is required')
    if not source.startswith('http://'):
        source = config['ckan.site_url'] + source.strip('/')
    source = urlparse.urlparse(source)

    dtype = data_dict.get('dtype', 'inspire')

    try:
        owner_org = data_dict['owner_org']
    except KeyError:
        raise ValueError(
            'The `owner_org` parameter is required.\n'
            'Hint: Use organization_list_for_user action to retrieve a valid list')
        
    allow_rename = data_dict.get('on_name_conflict', 'abort') == 'rename'
    allow_validation_errors = data_dict.get('on_errors', 'continue') == 'continue'

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
        raise toolkit.Invalid(_('The given XML file is malformed'))

    # Prepare package dict
    
    pkg_dict = obj.deduce_basic_fields()
    pkg_dict.update({ 
        'dataset_type': dtype,
        dtype: obj.to_dict(flat=False),
    })
    
    # Find and assign a machine-name for this package
    # Note We just find the first available name, of course this does not guarantee
    # that it will remain available the actual time `package_create` is called.
    
    basename = pkg_dict['name']
    max_num_probes = 10 if allow_rename else 0
    name = _find_a_package_name(context, basename, max_num_probes)
    if not name:
        raise ValueError(
            'The package name %r is not available ' % (basename))
    else:
        pkg_dict['name'] = name
        pkg_dict['title'] += ' ' + name[len(basename):]
    
    # Create/Update package
    
    validation_errors, error_message = None, None

    ctx = _make_context(context)
    check_access('package_create', ctx, dict(name=name))
    try:
        pkg_dict = get_action('package_create')(ctx, data_dict=pkg_dict)
    except toolkit.ValidationError as ex:
        if 'name' in ex.error_dict:
            # The name is taken, re-raise exception
            raise ex
        elif allow_validation_errors:
            validation_errors = ex.error_dict
            error_message = ex.message or _('The dataset contains invalid metadata')
            # Retry `package_create` with a different context
            ctx = _make_context(context, skip_validation=True)
            check_access('package_create', ctx, dict(name=name))
            pkg_dict = get_action('package_create')(ctx, data_dict=pkg_dict)
            log1.warn('Created invalid package (skip-validation) as %r ' % (name))
        else:
            raise ex

    assert name == pkg_dict['name']
    
    return {
        # Provide basic package fields
        'id': pkg_dict['id'], 
        'name': name, 
        'state': pkg_dict.get('state'),
        # Provide details on validation (only if allow_validation_errors)
        'validation': {
            'message': error_message,
            'errors': validation_errors,
        },
    }

def _make_context(context, **opts):
    '''Make a new context for an action, based on an initial context.
    
    This is needed in case we want to retry the action, because re-using the
    previous context leads to strange errors (updates instead of creates etc?) 
    '''
    
    ctx = { 
        'model': context['model'], 
        'session': context['session'], 
        'user': toolkit.c.user,
    }
    
    if 'api_version' in context:
        ctx['api_version'] = context['api_version']

    ctx.update(opts)
    
    return ctx

def _find_a_package_name(context, basename, max_num_probes=12):
    '''Probe until you find an available (non-occupied) package name.
    
    The result name will be based on `name` and will try to append a suffix
    until it succeeds or until it reaches `max_num_probes`.

    If you pass a zero value for `max_num_probes`, it will essentially test if the given
    name (unmodified) is available (and will also return it).
    '''
    
    suffix_fmt = '~{num_probes:d}'
   
    ctx = _make_context(context, return_id_only=True)
    name, num_probes, found, exhausted = basename, 0, False, False
    while not (found or exhausted):
        try:
            check_access('package_show', ctx, dict(id=name))
            get_action('package_show')(ctx, data_dict=dict(id=name))
        except toolkit.ObjectNotFound:
            found = True
        else:
            if num_probes < max_num_probes:
                # Rename and retry
                num_probes += 1
                name = basename + suffix_fmt.format(num_probes=num_probes) 
            else:
                exhausted = True
   
    return name if found else None

