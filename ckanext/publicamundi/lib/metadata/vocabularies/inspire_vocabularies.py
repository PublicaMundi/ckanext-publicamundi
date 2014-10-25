import os
import re
import json
from datetime import datetime
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi import reference_data
from ckanext.publicamundi.lib.metadata.vocabularies import vocabularies

DATA_FILE = 'inspire-vocabularies.json'

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
    '''Load the module-global vocabularies dict from JSON data. 
    '''

    data_file = reference_data.get_path(DATA_FILE)

    data = None
    with open(data_file, 'r') as fp:
        data = json.loads(fp.read())

    for title in (set(data.keys()) - set(['Keywords'])):
        name = munge(title)
        vocabularies[name] = {
            'name': name,
            'title': title,
            'vocabulary': make_vocabulary(data.get(title).get('terms'))
        }

    keywords_data = data.get('Keywords')
    for title in keywords_data.keys():
        keywords = keywords_data.get(title)
        keywords_terms = make_vocabulary(keywords.get('terms'))

        name = munge('Keywords-' + title)
        vocabularies[name] = {
            'name': name,
            'title': title,
            'reference_date': datetime.strptime(keywords.get('reference_date'), '%Y-%m-%d').date(),
            'date_type': keywords.get('date_type'),
            'version': keywords.get('version'),
            'vocabulary': make_vocabulary(keywords.get('terms'))
        }

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

## Load vocabularies from JSON data

make_vocabularies()
