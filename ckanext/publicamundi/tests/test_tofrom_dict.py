import zope.interface
import zope.schema
import json
import copy
import dictdiffer
from datetime import date, time, datetime
from itertools import chain

from ckanext.publicamundi.lib.metadata.base import (
    Object, serializer_for_object,
    serializer_for_field, serializer_for_key_tuple)
from ckanext.publicamundi.lib.dictization import flatten
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.tests import fixtures
from ckanext.publicamundi.tests.helpers import assert_equal, diff_dicts

leaf_types = (basestring, bool, int, long, float,)

def test_objects_update_foo():
    
    for name in ['foo1', 'foo2', 'foo3', 'foo4']:
        for changeset in foo_updates.keys():
            yield _test_objects_update_foo, name, changeset 

def _test_objects_update_foo(fixture_name, changeset):

    x0 = getattr(fixtures, fixture_name)
    assert isinstance(x0, types.Foo)
    df0 = x0.to_dict(flat=1, opts={'serialize-keys': 1})
    
    d = foo_updates[changeset]
    df = flatten(d, lambda k: '.' . join(map(str, k)))
   
    # Test shallow updates
    
    x1 = copy.deepcopy(x0)
    x1.from_dict(d, is_flat=0, opts={ 'update': True })
    df1 = x1.to_dict(flat=1, opts={'serialize-keys': 1})

    for k in (set(x0.get_fields()) - set(d.keys())):
        assert_equal(getattr(x1,k), getattr(x0,k))
 
    for change, key, desc in dictdiffer.diff(df0, df1):
        if change == 'change':
            val0, val1 = desc
            assert df[key] == val1
            assert df1[key] == val1
            assert df0[key] == val0
        elif change == 'add':
            for key1, val1 in desc:
                assert df[key1] == val1
                assert df1[key1] == val1
                assert not key1 in df0
        elif change == 'remove':
            for key0, val0 in desc:
                assert df0[key0] == val0
                assert not key0 in df1
                assert (not key0 in df) or (df[key0] is None) 

    # Test deep updates

    x2 = copy.deepcopy(x0)
    x2.from_dict(d, is_flat=0, opts={ 'update': 'deep' })
    
    for k in (set(x0.get_fields()) - set(d.keys())):
        assert_equal(getattr(x2,k), getattr(x0,k))
   
    df2 = x2.to_dict(flat=1, opts={'serialize-keys': 1})
    for change, key, desc in dictdiffer.diff(df0, df2):
        if change == 'change':
            val0, val2 = desc
            assert val2 == df[key]
            assert val0 == df0[key]
            assert val2 == df2[key]
        elif change == 'add':
            for key2, val2 in desc:
                assert key2 in df.keys()
                assert df2[key2] == val2
        elif change == 'remove':
            for key0, val0 in desc:
                assert df[key0] is None
                assert df0[key0] == val0
    
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

# Fixtures

foo_updates = {
    'upd-1': {
        'rating': None,
        'temporal_extent' : { 'start': date(1999,1,1), },
        'tags': [ u'abrahatabra', u'baobab' ],
        'grade': 5.33,
        'contacts': { 
            'personal': { 
                'email': 'malex@example.com', 
                'address': { 'address': u'Sahara Desert', 'postalcode': u'11223' } } },
    },
    'upd-2': {
        'created': datetime(2014, 9, 1),
        'contacts': { 
            'personal': { 
                'address': { 'address': u'Sahara Desert', 'postalcode': u'11223' } } },
    },
    'upd-3': {
        'created': datetime(2015, 9, 1),
        'contacts': { 
            'personal': { 
                'address': { 'address': u'Sahara Desert', } } },
    },
    'upd-4': {
        'baz': u'Baaaobab',
        'geometry': [[ 
            {
                'points': [
                    {'y': 1.8, 'x': 3.6}, {'y': 5.2, 'x': 1.5}, {'y': 7.2, 'x': 1.2}, {'y': 1.8, 'x': 3.6} ], 
                'name': u'Poly1-3'
            },
        ]]
    },
    'upd-5':{
        'geometry': [[
            {
                'points': [
                    {'y': 1.8, 'x': 3.6}, {'y': 5.2, 'x': 1.5}, {'y': 7.2, 'x': 1.2}, {'y': 1.8, 'x': 3.6} ], 
                'name': u'Poly1-4'
            },
            {
                'points': [
                    {'y': 1.0, 'x': 3.6}, {'y': 2.7, 'x': 9.1}, {'y': 2.7, 'x': 1.9}, {'y': 1.0, 'x': 3.6} ], 
                'name': u'Poly2-4'
            },
        ]]
    },
    'upd-6': {
        'baz': u'Baaaobab',
        'tags': [ u'abrahatabra', u'baobab', u'test-1', u'test-2', u'test-3' ],
    },
}

# Main 

if __name__ == '__main__':
    
    _test_objects_update_foo('foo2', 'upd-4')
    
    for t, x, y in test_objects():
        t(x, y)

