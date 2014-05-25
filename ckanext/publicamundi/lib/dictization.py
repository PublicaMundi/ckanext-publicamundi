import itertools
import logging

def flatten(d, key_converter=None):
    '''Flatten a dictionary'''
    res = None
    d1 = _flatten_items(d.iteritems())
    if key_converter and callable(key_converter):
        res = { key_converter(k):v for k,v in d1.items() }
    else:
        res = d1
    return res

def nest(d, key_converter=None):
    '''Unflatten a dictionary'''
    res = None
    if key_converter and callable(key_converter):
        d1 = { key_converter(k):v for k,v in d.items() }
    else:
        d1 = d
    res = _nest(d)
    return res

unflatten = nest 

def _nest(d):
    keys = sorted(d)
    # Collect all pairs (k,res1) for this level
    pairs = list()
    is_list, i1, i = True, -1, None
    for k,g in itertools.groupby(keys, lambda t: t[0]):
        # Guess the key type (update is_list flag)
        if is_list:
            # We have'nt (yet) discovered a non-index key  
            i = _as_integer(k)
            is_list = isinstance(i, int) and (i == i1 +1)
            i1 = i
        # Create another pair
        d1 = dict()
        for k1 in g:
            d1[k1[1:]] = d[k1]
        if d1.has_key(()):
            res1 = d1.pop(())
        else:
            res1 = _nest(d1)
        pairs.append((k, res1))
    # Build result to proper type (dict/list)
    res = None
    if is_list:
        res = [ v for k, v in sorted(pairs) ]
    else:
        res = dict(pairs)
    return res

def _flatten_items(items):
    ''' A simple flattening routine based on the type of each value item.'''
    res = {}
    for k,v in items:
        # Detect value type
        it1 = None
        if isinstance(v, dict):
            it1 = v.iteritems()
        elif isinstance(v, list) or isinstance(v, tuple):
            it1 = enumerate(v)
        # Decide if we must descent
        if it1:
            res1 = _flatten_items(it1)
            for k1,v1 in res1.items():
                res[(k,)+k1] = v1
        else:
            res[(k,)] = v
    return res

def _as_integer(x):
    n = None
    try:
        n = int(x)
    except ValueError:
        pass
    return n
