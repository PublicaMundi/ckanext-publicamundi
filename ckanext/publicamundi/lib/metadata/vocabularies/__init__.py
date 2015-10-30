'''
These exported vocabularies are intended to be read-only instances of zope
SimpleVocabulary. In most cases, there will be no need to access directly 
(but via the read-only API or via Thesaurus properties).
'''

vocabularies = {}

# Import loader

from ckanext.publicamundi.lib.metadata.vocabularies.json_loader import (
    make_vocabularies, normalize_keyword, normalize_thesaurus_title)

def _update(data_file, name_prefix='', overwrite=False):
    '''Update the module-global vocabularies from external JSON data.
    '''
    for name, desc in make_vocabularies(data_file):
        assert overwrite or not (name in vocabularies), (
            'A vocabulary named %r is already loaded' % (name))
        vocabularies[name_prefix + name] = desc

# Utilities

def get_titles():
    return { k: vocabularies[k]['title'] for k in vocabularies }

def get_names():
    return vocabularies.keys()

def get_by_title(title):
    keys = filter(lambda t: vocabularies[t]['title'] == title, vocabularies.keys())
    if keys:
        k = keys[0]
        return vocabularies[k]
    else:
        return None

def get_by_name(name):
    return vocabularies.get(name)

# Initialize - Load common vocabularies

from ckanext.publicamundi import reference_data

_update(
    reference_data.get_path('inspire-vocabularies.json'), 
    name_prefix='')

_update(
    reference_data.get_path('language-codes.json'), 
    name_prefix='')

