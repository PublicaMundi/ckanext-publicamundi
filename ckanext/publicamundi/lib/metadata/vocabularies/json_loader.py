import os
import re
import json
from datetime import datetime
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

def _munge(name):
    '''Convert human-friendly to machine-friendly names.
    '''

    re_bad = re.compile('[\(\),]+')
    re_delim = re.compile('[ \/\t_-]+')
    
    name = str(name)
    name = name.lower()
    name = re_bad.sub('', name)
    name = re_delim.sub('-', name)
    name = name.replace('&', '-and-')

    return name

def normalize_keyword(name):
    return _munge(name)

def normalize_thesaurus_title(name, for_keywords=False):
    if not for_keywords:
        return _munge(name)
    else:
        return _munge('keywords' + ' ' + name)

def make_vocabulary(data):
    '''Convert raw data to a SimpleVocabulary instance.
    
    The input data can be one of the following:
     * a list of human-readable terms or a
     * a dict that maps machine-readable to human-readable terms.
    '''
    
    terms = []
    if isinstance(data, list):
        for t in data:
            k = normalize_keyword(t)
            terms.append(SimpleTerm(k, t, t))
    elif isinstance(data, dict):     
        for k, t in data.items():
            #k = normalize_keyword(k)
            terms.append(SimpleTerm(k, t, t))
    return SimpleVocabulary(terms, swallow_duplicates=True)

def make_vocabularies(data_file):
    '''Load vocabularies from JSON data.

    Return tuples of (<name>, <vocabulary-descriptor>).
    '''

    data = None
    with open(data_file, 'r') as fp:
        data = json.loads(fp.read())

    for title in (set(data.keys()) - set(['Keywords'])):
        name = normalize_thesaurus_title(title)
        desc = {
            'name': name,
            'title': title,
            'vocabulary': make_vocabulary(data.get(title).get('terms'))
        }
        yield (name, desc)

    keywords_data = data.get('Keywords')
    for title in keywords_data.keys():
        keywords = keywords_data.get(title)
        keywords_terms = make_vocabulary(keywords.get('terms'))
        name = normalize_thesaurus_title(title, for_keywords=True)
        desc = {
            'name': name,
            'title': title,
            'reference_date': datetime.strptime(keywords.get('reference_date'), '%Y-%m-%d').date(),
            'date_type': keywords.get('date_type'),
            'version': keywords.get('version').encode('utf-8'),
            'vocabulary': make_vocabulary(keywords.get('terms'))
        }
        yield (name, desc)

