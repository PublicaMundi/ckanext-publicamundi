import os
import re
import json
from datetime import datetime
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

def munge(name):
    '''Convert human-friendly to machine-friendly terms.
    
    Needed when a machine-friendly version is not supplied.
    '''

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
            #k = munge(k)
            terms.append(SimpleTerm(k, k, t))
    return SimpleVocabulary(terms, swallow_duplicates=True)

def make_vocabularies(data_file):
    '''Load vocabularies from JSON data.

    Return tuples of (<name>, <vocabulary-descriptor>).
    '''

    data = None
    with open(data_file, 'r') as fp:
        data = json.loads(fp.read())

    for title in (set(data.keys()) - set(['Keywords'])):
        name = munge(title)
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

        name = munge('Keywords-' + title)
        desc = {
            'name': name,
            'title': title,
            'reference_date': datetime.strptime(keywords.get('reference_date'), '%Y-%m-%d').date(),
            'date_type': keywords.get('date_type'),
            'version': keywords.get('version').encode('utf-8'),
            'vocabulary': make_vocabulary(keywords.get('terms'))
        }
        yield (name, desc)

