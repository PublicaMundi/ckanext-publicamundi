import datetime
from beaker.cache import (cache_regions, cache_region)

import ckan.model as model
import ckan.plugins.toolkit as toolkit

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

