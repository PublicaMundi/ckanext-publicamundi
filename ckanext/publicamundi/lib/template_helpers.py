import operator
import datetime

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib import resource_ingestion

def filtered_list(l, key, value, op='eq'):
    '''Filter list items based on their value in a specific key/attr.
    '''

    if not l:
        return None
    
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
    return dict((org['name'], org) for org in orgs )

def resource_ingestion_result(resource_id):
    return resource_ingestion.get_result(resource_id)

