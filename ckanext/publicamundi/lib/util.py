import random
import string
import json
import geojson
import shapely
import collections
import itertools
from dictdiffer import (
    dot_lookup, diff as diff_dicts, patch as patch_dict)

from ckanext.publicamundi.lib.json_encoder import JsonEncoder

class Breakpoint(Exception):
    '''Exception used for Pylons debugging'''
    pass

def to_json(o, indent=None):
    '''Convert to JSON providing our custom encoder'''
    return json.dumps(o, cls=JsonEncoder, indent=indent)

def geojson_to_wkt(s):
    from shapely.geometry import shape
    g = shape(geojson.loads(s))
    return g.wkt

def geojson_to_wkb(s):
    from shapely.geometry import shape
    g = shape(geojson.loads(s))
    return g.wkb

def wkt_to_geojson(s):
    from shapely.wkt import loads as wkt_loads
    g = geojson.Feature(geometry=wkt_loads(s))
    return str(g.geometry)

def random_name(l):
    return random.choice(string.lowercase) + \
        ''.join(random.sample(string.lowercase + string.digits, int(l)-1))

def stringify_exception(ex):
    return '%s: %s' %(type(ex).__name__, str(ex).strip())

def raise_for_stub_method():
    raise NotImplementedError('Method should be implemented in a derived class')

def quote(s):
    '''A naive routine to enclose a unicode string in double quotes'''
    return u'"' + s.replace('\\', '\\\\').replace('"', '\\"') + u'"'

def find_all_duplicates(l):
    counter = collections.Counter(l)
    dups = { k:n for k,n in counter.items() if n > 1 }
    return dups

def attr_setter(o, k):
    def f(v):
        setattr(o, k, v)
    return f
 
def item_setter(d, k):
    def f(v):
        d[k] = v
    return f

def const_function(val):
    '''Create a const function'''
    return itertools.repeat(val).next 

class falsy_function(object):
    '''Create a function marked as falsy'''

    def __call__(self, *args, **kwargs):
        assert False, 'This is not supposed to be called'
    
    def __repr__(self):
        return '<not-a-function>'

    def __nonzero__(self): 
        return False

not_a_function = falsy_function()

