import os
import re
import json
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# Babel string extraction functions

def extract_json(fileobj, keywords, comment_tags, options):
    """Extract messages from XXX files.
    :param fileobj: the file-like object the messages should be extracted from
    :param keywords: a list of keywords (i.e. function names) that should be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)`` tuples
    :rtype: ``iterator``

    file structure with all possible sub-structures

    {
    'vocab1':{
        'terms':[i1, i2, i3]
        },
    'vocab2':{
        'terms':{k1:v1, k2:v2, k3:v3}
        },
    'vocab3':{
        'Thes1':{
            'meta-1':'X',
            'meta-2':'Y',
            'terms':[i1, i2, i3],
        },
        'Thes2':{
            'meta-1':'X',
            'meta-2':'Y',
            'terms':[i1, i2, i3],
            },
        }
    }
    """

    i = 0
    for k,v in json.loads(fileobj.read()).iteritems():
        i += 1
        if isinstance(v, dict):
            for kk,vv in v.iteritems():
                i += 1

                if kk == 'terms':
                    # Case 1 Dictionary with list of values (vocab1)
                    if isinstance(vv, list):
                        for vvv in vv:
                            i += 1
                            yield (i, 0, vvv, "")

                    # Case 2 Simple key,value dictionary (vocab2)
                    elif isinstance(vv, dict):
                        for kkk,vvv in vv.iteritems():
                            i += 1
                            yield (i, 0, vv, "")

                else:
                    # Case 3 Dictionary with metadata and list of values
                    for kkkk,vvvv in vv.iteritems():
                        i += 1

                        if kkkk == 'terms':
                            if isinstance(vvvv, list):
                                for vvvvv in vvvv:
                                    i += 1
                                    yield (i, 0, vvvvv, "")

