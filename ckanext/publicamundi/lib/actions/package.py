import os
import errno
import fcntl
import logging
import datetime
import requests
import urlparse

from pylons import g, config

import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.lib.uploader import get_storage_path

from ckanext.publicamundi.cache_manager import get_cache
from ckanext.publicamundi.lib.actions import (NameConflict, InvalidParameter)
from ckanext.publicamundi.lib.metadata import (
    dataset_types,
    make_metadata_object,
    serializer_for,
    xml_serializer_for)

log = logging.getLogger(__name__)

_ = toolkit._
_get_action = toolkit.get_action
_check_access = toolkit.check_access

@logic.side_effect_free
def dataset_export(context, data_dict):
    '''Export a dataset to XML.
    
    :param id: the name or id of the dataset to be exported.
    :type id: string

    rtype: string
    '''

    _check_access('package_show', context, data_dict)
    pkg = _get_action('package_show')(context, data_dict)
    
    dtype = pkg.get('dataset_type')
    obj = pkg.get(dtype) if dtype else None
    
    cached_metadata = get_cache('metadata') 
    result = None
    if obj:
        # Get a proper serializer
        xser = xml_serializer_for(obj)
        xser.target_namespace = config.get('ckan.site_url') 
        # Persist exported XML data and wrap into a URL
        name = '%(name)s@%(revision_id)s' % (pkg)
        cached = cached_metadata.get(name, createfunc=xser.dumps)
        link = toolkit.url_for(
            controller='ckanext.publicamundi.controllers.files:Controller',
            action='download_file', 
            object_type='metadata',
            name_or_id=name,
            filename=('%(name)s.xml' % (pkg)))
        result = dict(url=link)
    
    return result

def dataset_import(context, data_dict):
    '''Import a dataset from a given XML source.

    This action, depending also on the value of its flags, can raise one of:
      * actions.InvalidParameter: received an invalid parameter
      * actions.NameConflict: a package name conflict is encountered
      * toolkit.Invalid: received a source XML file that is not parse-able
      * toolkit.ValidationError: validation fails while trying to create a package 

    :param source: This is either a string representing a (local or external) URL 
        or a file-like object.
    :type q: string or file-like
    
    :param dtype: the dataset-type i.e. the schema of imported metadata
    :type dtype: string

    :param owner_org: the machine-name for the owner organization 
    :type owner_org: string

    :param continue_on_errors: hint on what to do when validation fails
    :type continue_on_errors: boolean
    
    :param rename_if_conflict: hint on what to do when a name conflict is encountered
    :type rename_if_conflict: boolean

    :rtype: basic info for the newly created package 
    '''
      
    # Read parameters

    try:
        source = data_dict['source']
    except KeyError:
        raise InvalidParameter('The `source` parameter is required', 'source')
    
    dtype = data_dict.get('dtype', 'inspire')

    try:
        owner_org = data_dict['owner_org']
    except KeyError:
        raise InvalidParameter(
            'The `owner_org` parameter is required.\n'
                'Hint: Use `organization_list_for_user` to retrieve a valid list.',
            'owner_org')
        
    allow_rename = data_dict.get('rename_if_conflict', False)
    allow_validation_errors = data_dict.get('continue_on_errors', False)

    # Fetch raw XML data
    
    xmldata = None
    
    if isinstance(source, basestring):
        # Assume source is a URL
        if not source.startswith('http://'):
            source = config['ckan.site_url'] + source.strip('/')
        source = urlparse.urlparse(source)
        r1 = requests.get(source.geturl())
        if not r1.ok:
            raise InvalidParameter(
                'Cannot fetch metadata from source URL', 'source')
        elif not r1.headers['content-type'] in ['application/xml', 'text/xml']:
            raise InvalidParameter(
                'The given source does not contain XML data', 'source')
        else:
            xmldata = r1.content
    else:
        # Assume source is a file-like object
        try:
            xmldata = source.read()
        except:
            raise InvalidParameter('Cannot read from source', 'source')

    # Parse XML data as metadata of `dtype` schema
    
    obj = make_metadata_object(dtype)
    try:
        obj = xml_serializer_for(obj).loads(xmldata)
    except Exception as ex:
        # Map all parse exceptions to Invalid (even assertion errors!)
        log.info('Failed to parse XML metadata: %s', ex)
        raise toolkit.Invalid(_('The given XML file is malformed: %s') % (ex))

    # Prepare package dict
    
    pkg_dict = obj.deduce_basic_fields()
    pkg_dict.update({ 
        'owner_org': owner_org,
        'type': 'dataset',
        'dataset_type': dtype,
        dtype: obj.to_dict(flat=False),
    })
    
    # Find and assign a machine-name for this package
    # Note We just find the 1st available name, of course this does not guarantee
    # that it will remain available the actual time package_create is called.
    
    basename = pkg_dict['name']
    max_num_probes = 10 if allow_rename else 1
    name = _find_a_package_name(context, basename, max_num_probes)
    if not name:
        raise NameConflict(
            'The package name %r is not available ' % (basename))
    else:
        pkg_dict['name'] = name
        pkg_dict['title'] += ' ' + name[len(basename):]
    
    # Create/Update package
    
    validation_errors, error_message = None, None

    ctx = _make_context(context)
    _check_access('package_create', ctx, dict(name=name))
    try:
        pkg_dict = _get_action('package_create')(ctx, data_dict=pkg_dict)
    except toolkit.ValidationError as ex:
        if 'name' in ex.error_dict:
            # The name is probably taken, re-raise exception
            raise ex
        elif allow_validation_errors:
            # Save errors and retry with a different context
            validation_errors = ex.error_dict
            error_message = ex.message or _('The dataset contains invalid metadata')
            ctx = _make_context(context, skip_validation=True)
            _check_access('package_create', ctx, dict(name=name))
            pkg_dict = _get_action('package_create')(ctx, data_dict=pkg_dict)
            log.warn('Forced to create an invalid package as %r ' % (name))
        else:
            raise ex

    assert name == pkg_dict['name']
    
    return {
        # Provide basic package fields
        'id': pkg_dict['id'], 
        'name': name,
        'title': pkg_dict['title'],
        'state': pkg_dict.get('state'),
        # Provide details on validation (meaningfull if allow_validation_errors)
        'validation': {
            'message': error_message,
            'errors': validation_errors,
        },
    }

def _make_context(context, **opts):
    '''Make a new context for an action, based on an initial context.
    
    This is needed in case we want to retry a same action, because re-using the
    previous context can lead to strange errors (updates instead of creates etc) 
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

    If you pass 1 as value for `max_num_probes`, it will essentially test if the given
    name (unmodified) is available (and will also return it).
    '''
    
    suffix_fmt = '~{num_probes:d}'
   
    ctx = _make_context(context, return_id_only=True)
    name, num_probes, found, exhausted = basename, 0, False, False
    while not (found or exhausted):
        try:
            num_probes += 1
            _check_access('package_show', ctx, dict(id=name))
            _get_action('package_show')(ctx, data_dict=dict(id=name))
        except toolkit.ObjectNotFound:
            found = True
        else:
            if num_probes < max_num_probes:
                # Rename and retry
                name = basename + suffix_fmt.format(num_probes=num_probes) 
            else:
                exhausted = True
   
    return name if found else None

