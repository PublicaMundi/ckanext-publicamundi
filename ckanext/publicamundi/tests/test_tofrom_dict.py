import zope.interface
import zope.schema
import json
import copy
import autopep8
import datadiff
from datadiff.tools import assert_equal
from datetime import date, time, datetime
from itertools import chain

from ckanext.publicamundi.lib.metadata.base import (
    Object, serializer_for_object,
    serializer_for_field, serializer_for_key_tuple)
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.tests import fixtures

leaf_types = (basestring, bool, int, long, float,)

pprint_code = lambda s: autopep8.fix_code(s, options=autopep8.parse_args(['-a', '']))

def test_objects_update_foo():

    yield _test_objects_update_foo, 'foo1' 

def _test_objects_update_foo(fixture_name):

    x0 = getattr(fixtures, fixture_name)
    assert isinstance(x0, types.Foo)
    
    d = {
        'rating': 9,
        'temporal_extent' : { 'start': date(1999,1,1), 'end': None },
        'tags': [ u'abrahatabra', u'baobab' ],
        'contacts': { 
            'personal': { 
                'email': 'malex@example.com', 
                'address': { 'address': u'Sahara Desert', 'postalcode': u'11223' } } },
    }
   
    # Update shallow
    
    x1 = copy.deepcopy(x0)
    x1.from_dict(d, is_flat=0, opts={ 'update': True })

    for k in (set(x0.get_fields()) - set(d.keys())):
        assert_equal(getattr(x1,k), getattr(x0,k))
 
    d1 = x1.to_dict(flat=0)
    for k in d.keys():
        assert_equal(d[k], d1[k]) 
    
    # Update deep

    x2 = copy.deepcopy(x0)
    x2.from_dict(d, is_flat=0, opts={ 'update': 'deep' })
    
    for k in (set(x0.get_fields()) - set(d.keys())):
        assert_equal(getattr(x2,k), getattr(x0,k))
   
    # Todo Find a clever way to use datadiff.diff_dict in order to
    # test deep updates!

    pass

def test_objects():
    
    tests = chain(
        _test_dictization('bbox1'),
        _test_dictization('contact1'),
        _test_dictization('foo1'),
    )
    
    for tester, fixture_name, opts in tests:
        yield tester, fixture_name, opts

def _test_flattened_dict(fixture_name, opts):

    x = getattr(fixtures, fixture_name)
    assert isinstance(x, Object)
    
    factory = type(x)

    # Dictize
    
    d = x.to_dict(flat=True, opts=opts)

    print
    print ' -- Dictize: flattened opts=%r' %(opts)
    print d

    key_type = basestring if opts.get('serialize-keys') else tuple
    key_prefix = opts.get('key-prefix')
    kser = serializer_for_key_tuple(key_prefix=key_prefix)
    
    for k in d:
        assert isinstance(k, key_type)
    
    expected_keys = x.get_flattened_fields().keys()

    max_depth = opts.get('max-depth')
    if max_depth is not None:
        assert max_depth > 0
        expected_keys = list(set(map(lambda t: t[0:max_depth], expected_keys)))

    if key_type is basestring:
        expected_keys = map(kser.dumps, expected_keys)
    
    for k in d:
        assert k in expected_keys

    if key_prefix:
        for k in d:
            assert k.startswith(key_prefix)

    if opts.get('serialize-values'):
        for v in d.itervalues():
            assert v is None or isinstance(v, leaf_types)

    # Load

    opts1 = { 
        'unserialize-keys': opts.get('serialize-keys', False),
        'unserialize-values': opts.get('serialize-values', False),
        'key-prefix': opts.get('key-prefix', None),
    }

    x1 = factory().from_dict(d, is_flat=True, opts=opts1)
    d1 = x1.to_dict(flat=True, opts=opts)
    
    assert_equal(d, d1)
    assert x == x1

def _test_nested_dict(fixture_name, opts):

    x = getattr(fixtures, fixture_name)
    assert isinstance(x, Object)
    
    factory = type(x)
    
    # Dictize

    d = x.to_dict(flat=False, opts=opts)

    assert set(d.keys()) == set(x.get_field_names())
    
    print
    print ' -- Dictize: nested opts=%r' %(opts)
    print d
    
    # Load
    
    opts1 = { 
        'unserialize-values': opts.get('serialize-values', False),
    }

    x1 = factory().from_dict(d, is_flat=False, opts=opts1)
    d1 = x1.to_dict(flat=False, opts=opts)

    assert_equal(d, d1)
    assert x == x1

def _test_dictization(fixture_name):

    opts = {}
    yield _test_nested_dict, fixture_name, opts
    yield _test_flattened_dict, fixture_name, opts
    
    opts = { 'serialize-keys': True }
    yield _test_flattened_dict, fixture_name, opts
    
    opts = { 'serialize-values': True }
    yield _test_nested_dict, fixture_name, opts
    yield _test_flattened_dict, fixture_name, opts
    
    opts = { 'serialize-values': 'json-s' }
    yield _test_nested_dict, fixture_name, opts
    yield _test_flattened_dict, fixture_name, opts
   
    opts = { 'serialize-keys': True, 'serialize-values': True }
    yield _test_flattened_dict, fixture_name, opts
    
    opts = { 'serialize-keys': True, 'serialize-values': 'json-s' }
    yield _test_flattened_dict, fixture_name, opts
    
    opts = { 'serialize-keys': True, 'key-prefix': 'test1', 'serialize-values': True }
    yield _test_flattened_dict, fixture_name, opts
   
    for n in range(1, 5):
        opts = { 'max-depth': n }
        yield _test_flattened_dict, fixture_name, opts
        opts = { 'serialize-keys': True, 'max-depth': n }
        yield _test_flattened_dict, fixture_name, opts
        opts = { 'serialize-keys': True, 'key-prefix': 'test1', 'max-depth': n }
        yield _test_flattened_dict, fixture_name, opts

if __name__ == '__main__':
    
    _test_objects_update_foo('foo1')
    
    for t, x, y in test_objects():
        t(x, y)

