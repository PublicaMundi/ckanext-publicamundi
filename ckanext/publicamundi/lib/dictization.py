import itertools
import collections

from collections import OrderedDict
from operator import itemgetter, attrgetter

def flatten(d, key_converter=None):
    '''Flatten a dictionary'''
    res = None
    d1 = _flatten_items(d.iteritems())
    if key_converter and callable(key_converter):
        res = { key_converter(k):v for k,v in d1.items() }
    else:
        res = d1
    return res

def unflatten(d, key_converter=None):
    '''Unflatten a dictionary'''
    res = None
    if key_converter and callable(key_converter):
        d1 = { key_converter(k):v for k,v in d.items() }
    else:
        d1 = d
    res = _unflatten(d)
    return res

def _unflatten(d):
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
            res1 = _unflatten(d1)
        pairs.append((k, res1))
    
    # Build result to proper type (dict/list)
    
    res = None
    if not pairs:
        res = dict()
    elif is_list:
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

def merge_inplace(a, b):
    '''Merge dict b into dict a. 
    The target dict a is modified in-place, while b remains untouched.
    '''

    ka = set(a.keys())
    kb = set(b.keys())
    
    for k in (kb - ka):
        a[k] = b[k]
    
    for k in (ka & kb):
        ak, bk = a[k], b[k]
        if isinstance(ak, dict) and isinstance(bk, dict):
            # Recurse
            merge_inplace(ak, bk)
        elif not isinstance(ak, dict) and not isinstance(bk, dict):
            # Treat as leafs, represent always as lists
            if not isinstance(ak, list):
                a[k] = [ak]
            a[k].extend(bk if isinstance(bk, list) else [bk])
        else:
            # Nop: cannot merge a dict with a non-dict
            pass
    
    # Return modified target (for convenience)   
    return a

def merge(a, b):
    '''Merge dicts a,b and return a new dict.
    None of the inputs is directly modified, but internal structure of
    a,b is not copied (but just referenced).
    '''

    if isinstance(a, dict) and isinstance(b, dict):
        ka = set(a.keys())
        kb = set(b.keys())
        res = dict()
        for k in (ka - kb):
            res[k] = a[k]
        for k in (kb - ka):
            res[k] = b[k]
        for k in (ka & kb):
            res[k] = merge(a[k], b[k])
        return res
    elif not isinstance(a, dict) and not isinstance(b, dict):
        if a is None:
            return b
        elif b is None:
            return a
        else:
            # both are not None
            la = a if isinstance(a, list) else [a]
            lb = b if isinstance(b, list) else [b]
            return la + lb
    else:
        # Cannot merge a dict with a non-dict, return a
        return a
   
def update_deep(a, b):
    '''Perform a deep update of a from b
    '''
    
    ka = set(a.keys())
    kb = set(b.keys())
    
    for k in (kb - ka):
        a[k] = b[k]

    for k in (ka & kb):
        ak, bk = a[k], b[k]
        if isinstance(ak, dict) and isinstance(bk, dict):
            ak = update_deep(ak, bk)
        else:
            a[k] = bk

    return a

def numbered(d, key_order=int):
    '''Try to convert a dict to an OrderedDict with numbered values.
    
    Each key is converted to an index according to `key_order`. If a key 
    fails to convert, the corresponding value is omitted.
    
    E.g.:
    {'0': 'aaa', '5': 'ccc', '4': 'bbb', 'a': 'AAA'} -> 
    OrderedDict((0, 'aaa'), (4, 'bbb'), (5, 'ccc'))
    '''
    
    a = []
    for k in d:
        i = None
        try:
            i = key_order(k)
        except:
            pass
        if isinstance(i, int):
            a.append((i, d[k]))  
    od = OrderedDict(sorted(a, key=itemgetter(0)))
    return od

def enumerated(d, key_order=int, missing_value=None):
    '''Try to convert a dict to an enumeration.
    
    Works like numbered, but returns an iterator on a continuous range
    of integers (mimics builtin enumerate iterator).
    '''
    
    od = numbered(d, key_order)
    
    m = next(reversed(od)) + 1
    for i in xrange(0, m):
        yield (i, od.get(i, missing_value))
    
