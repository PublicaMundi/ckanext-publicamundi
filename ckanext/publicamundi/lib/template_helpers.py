import operator
import datetime
import urlparse
import urllib

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import (
    fields, bound_field, markup_for_field, markup_for)
from ckanext.publicamundi.lib import resource_ingestion
from ckanext.publicamundi.lib.metadata import vocabularies

def filtered_list(l, key, value, op='eq'):
    '''Filter list items based on their value in a specific key/attr.
    '''

    if not l:
        return l
    
    op_map = {
        'ne': operator.ne,
        'eq': operator.eq,
        'le': operator.ge,
        'lt': operator.gt,
        'ge': operator.le,
        'gt': operator.lt,
        '!=': operator.ne,
        '==': operator.eq,
        '<=': operator.ge,
        '<':  operator.gt,
        '>=': operator.le,
        '>':  operator.lt,
        'in': operator.contains,
        'not-in': lambda a, b: not operator.contains(a, b) 
    }
   
    op = op_map.get(str(op).lower(), operator.eq)

    items_are_dicts = operator.isMappingType(l[0])
    if items_are_dicts:
        def pred(x):
            return op(value, x.get(key))
    else:
        def pred(x):
            return op(value, getattr(x, key, None))
    
    return filter(pred, l)

def get_organization_objects(org_names=[]):
    '''Fetch organizations as a dict (keyed to name) of fully-loaded objects
    '''
    
    context = {
        'model': model,
        'session': model.Session,
        'user': toolkit.c.user,
    }

    options = { 'all_fields': True }
    if org_names:
        t = type(org_names[0])
        if t is str:
            options['organizations'] = org_names
        elif t is dict:
            options['organizations'] = [org['name'] for org in org_names]

    orgs = toolkit.get_action('organization_list')(context, options)
    return { org['name']: org for org in orgs }

def resource_ingestion_result(resource_id):
    return resource_ingestion.get_result(resource_id)

def markup_for_translatable_text(key, value):
    uf = markup_for_translatable_text._text_field
    yf = bound_field(uf, key, value)
    qa = 'read:dd.translatable'
    return markup_for_field(qa, yf, name_prefix='')
markup_for_translatable_text._text_field = fields.TextField()
markup_for_translatable_text._text_field.setTaggedValue('translatable', True)

_preferable_metadata_format = [
        {'name':'INSPIRE',
         'format':'xml'},
        {'name': 'CKAN',
        'format': 'json'}]

_default_metadata_format = 'xml'

# Returns the most suitable primary download format for each schema
# based on _preferable_metadata_format list of dictionaries
def get_primary_metadata_url(links, metadata_type):
    pformat = _default_metadata_format

    for mtype in _preferable_metadata_format:
        if mtype.get('name') == metadata_type:
            pformat = mtype.get('format')

    url = ''
    for link in links:
        if link.get('title') == metadata_type and link.get('format') == pformat:
            url = link.get('url')
            break
    return url

def get_ingested_raster(package,resource):
    ing_resources = []
    for res in package.get('resources'):
        if res.get('rasterstorer_resource') and res.get('parent_resource_id')==resource.get('id'):
            ing_resources.append(res)
    return ing_resources

def get_ingested_vector(package,resource):
    ing_resources = []
    for resa in package.get('resources'):
        # Ingested vector resources are derived from table which is derived from resource
        # Finding all resources that are ingested from table that is created from original resource
        if resa.get('vectorstorer_resource') and resa.get('parent_resource_id')==resource.get('id') and resa.get('format')=='data_table':
            for resb in package.get('resources'):
                if resb.get('vectorstorer_resource') and resb.get('parent_resource_id')==resa.get('id'):
                    ing_resources.append(resb)
    return ing_resources

def transform_to_iso_639_2(langcode_iso_639_1):
    
    languages_iso_639_1 = vocabularies.get_by_name('languages-iso-639-1')
    languages_iso_639_2 = vocabularies.get_by_name('languages-iso-639-2')
  
    token = languages_iso_639_1.get('vocabulary').by_value.get(langcode_iso_639_1).title
    value = languages_iso_639_2.get('vocabulary').by_token.get(token).value
    
    return value
