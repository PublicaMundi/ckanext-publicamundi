import os
import re
import json
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collections import OrderedDict

# Babel string extraction functions

def extract_json(fileobj, keywords, comment_tags, options):
    """Extract messages from files.
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
    line = 0
    values = json.loads(fileobj.read(), object_pairs_hook=OrderedDict)

    for k, v in values.iteritems():
        line += 1
        if isinstance(k, unicode) or isinstance(k, str):
            line += 1
            yield(line, 0, str(k), "")

        if isinstance(v, OrderedDict):
            for kk,vv in v.iteritems():
                line += 1

                if kk == 'terms':
                    # Case 1 Dictionary with list of values (vocab1)
                    if isinstance(vv, list):
                        for vvv in vv:
                            line += 1
                            yield (line, 0, str(vvv), "")

                    # Case 2 Simple key,value dictionary (vocab2)
                    elif isinstance(vv, OrderedDict):
                        for kkk,vvv in vv.iteritems():
                            line += 1
                            yield (line, 0, str(vvv), "")

                else:
                    # Case 3 Dictionary with metadata and list of values
                    for kkk,vvv in vv.iteritems():
                        line += 1

                        if kkk == 'terms':
                            if isinstance(vvv, list):
                                for vvvv in vvv:
                                    line += 1
                                    yield (line, 0, str(vvvv), "")
                    line += 1
                line += 1
