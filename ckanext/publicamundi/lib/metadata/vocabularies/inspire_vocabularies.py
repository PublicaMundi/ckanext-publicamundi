import os
import re
import json
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

DATA_FILE = 'inspire_vocabularies.json'

# Note: 
# These exported vocabularies are intended to be read-only instances
# of SimpleVocabulary. In most cases, there will be no need to access
# directly (but via Thesaurus properties).

vocabularies = {}

## Helpers

def munge(name):
    ''' Convert human-friendly to machine-friendly names'''
    
    re_bad = re.compile('[\(\),]+')
    re_delim = re.compile('[ \t_-]+')
    
    name = str(name)
    name = name.lower()
    name = re_bad.sub('', name)
    name = re_delim.sub('-', name)
    name = name.replace('&', '-and-')

    return name

def make_vocabulary(data):
    '''Convert raw data to a SimpleVocabulary instance.
    
    The input data can be one of the following:
     * a list of human-readable terms or a
     * a dict that maps machine-readable to human-readable terms.
    
    '''
    
    terms = []

    if isinstance(data, list):
        for t in data:
            k = munge(t)
            terms.append(SimpleTerm(k, k, t))
    elif isinstance(data, dict):     
        for k, t in data.items():
            k = munge(k)
            terms.append(SimpleTerm(k, k, t))

    return SimpleVocabulary(terms, swallow_duplicates=True)

def make_vocabularies():
    '''Load the module-global vocabularies dict with JSON data. 
    '''

    path = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(path, DATA_FILE)

    data = None
    with open(data_file, 'r') as fp:
        data = json.loads(fp.read())

    for name in (set(data.keys()) - set(['Keywords'])):
        k = munge(name)
        vocabularies[k] = {
            'name': name,
            'vocabulary': make_vocabulary(data.get(name))
        }

    keywords_data = data.get('Keywords')
    for name in keywords_data.keys():
        k = munge('Keywords-' + name)
        vocabularies[k] = {
            'name': name,
            'vocabulary': make_vocabulary(keywords_data.get(name).get('terms'))
        }

def get_names():
    return [ vocabularies[k]['name'] for k in vocabularies ]

def get_machine_names():
    return vocabularies.keys()

def get_by_name(name):
    keys = filter(lambda t: vocabularies[t]['name'] == name, vocabularies.keys())
    if keys:
        k = keys[0]
        return vocabularies[k]['vocabulary']
    else:
        return None

def get_by_machine_name(k):
    spec = vocabularies.get(k)
    return spec['vocabulary'] if spec else None

## Load vocabularies from JSON data

make_vocabularies()

