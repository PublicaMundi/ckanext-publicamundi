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
    'vocab1':[i1, i2, i3],
    'vocab2':{k1:v1, k2:v2, k3:v3},
    'vocab3':{k1:[i1, i2, i3], k2:[i1, i2, i3]}
    }
    """
    i = 0
    for k,v in json.loads(fileobj.read()).iteritems():
        i += 1
        # Case 1: Dictionary
        if isinstance(v,dict):
            for kk,vv in v.iteritems():
                i += 1

                # Case 1.1 Dictionary with value as list
                if isinstance(vv,list):
                    for vvv in vv:
                        i += 1
                        yield (i, 0, vvv, "")

                # Case 1.2 Simple key,value dictionary
                else:
                    yield (i, 0, vv, "")

        # Case 2: List
        elif isinstance(v,list):
            for vv in v:
                i += 1
                yield (i, 0, vv, "")
        #else:
        #    yield (i, 0, v, "")
