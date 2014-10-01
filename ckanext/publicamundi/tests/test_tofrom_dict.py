import nose.tools
import zope.interface
import zope.schema
import json
import copy
import dictdiffer
from datetime import date, time, datetime
from itertools import chain

from ckanext.publicamundi.lib.util import dot_lookup, diff_dicts
from ckanext.publicamundi.lib.metadata.base import (
    Object, serializer_for_object,
    serializer_for_field, serializer_for_key_tuple)
from ckanext.publicamundi.lib.dictization import flatten
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.tests import fixtures
from ckanext.publicamundi.tests.helpers import assert_equal

leaf_types = (basestring, bool, int, long, float,)

#
# Tests
#

@nose.tools.istest
def test_dictize_update_foo_discard_junk():

    for name in ['foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6', 'foo7']:
        for changeset in updates['foo'].keys():
            yield _test_dictize_update_discard_junk, name, 'foo', changeset 

@nose.tools.istest
def test_dictize_update():
    
    for name in ['foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6', 'foo7']:
        for changeset in updates['foo'].keys():
            yield _test_dictize_update, name, 'foo', changeset 
    
    for name in ['inspire1']:
        for changeset in updates['inspire'].keys():
            yield _test_dictize_update, name, 'inspire', changeset 

def _test_dictize_update_discard_junk(fixture_name, dtype, changeset):
    
    key_prefix = 'fooo'

    x0 = getattr(fixtures, fixture_name)
    assert isinstance(x0, types.Foo)
    d = updates[dtype][changeset]

    # Prepend a key-prefix, and then insert some junk items into df
    
    df = flatten(d, lambda k: '.' . join(map(str, k)))

    af = []
    af.extend([ ('%s.%s' % (key_prefix, k), v) for k, v in df.items() ])
    af.extend([ ('a', 99), ('junk.1', 'something'), ('z.aa', 100), (key_prefix, 'baobab') ])
    df = dict(af)

    # Load   
    
    x1 = copy.deepcopy(x0)
    x1.from_dict(d, is_flat=0, opts={})

    x2 = copy.deepcopy(x0)
    x2.from_dict(df, is_flat=1, opts={
        'unserialize-keys': 1, 'key-prefix': key_prefix })
    
    assert x1 == x2
    
    # Update in shallow mode 
    
    x1 = copy.deepcopy(x0)
    x1.from_dict(d, is_flat=0, opts={ 'update': 1 })

    x2 = copy.deepcopy(x0)
    x2.from_dict(df, is_flat=1, opts={
        'update': 1, 'unserialize-keys': 1, 'key-prefix': key_prefix })
    
    assert x1 == x2
   
    # Update in deep mode 
    
    x1 = copy.deepcopy(x0)
    x1.from_dict(d, is_flat=0, opts={ 'update': 'deep' })

    x2 = copy.deepcopy(x0)
    x2.from_dict(df, is_flat=1, opts={
        'update': 'deep', 'unserialize-keys': 1, 'key-prefix': key_prefix })
 
    assert x1 == x2

def _test_dictize_update(fixture_name, dtype, changeset):

    x0 = getattr(fixtures, fixture_name)
    assert x0
    df0 = x0.to_dict(flat=1, opts={'serialize-keys': 1})
    
    d = updates[dtype][changeset]
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
            assert ((val1 is None) and not (key in df)) or df[key] == val1
            assert df1[key] == val1
            assert df0[key] == val0
        elif change == 'add':
            for key1, val1 in desc:
                assert ((val1 is None) and not (key1 in df)) or df[key1] == val1
                assert df1[key1] == val1
                assert not key1 in df0
        elif change == 'remove':
            for key0, val0 in desc:
                assert df0[key0] == val0
                assert not key0 in df1
                assert not (key0 in df) or (df[key0] is None) 

    # Test deep updates

    x2 = copy.deepcopy(x0)
    x2.from_dict(d, is_flat=0, opts={ 'update': 'deep' })
    
    for k in (set(x0.get_fields()) - set(d.keys())):
        assert_equal(getattr(x2,k), getattr(x0,k))
   
    df2 = x2.to_dict(flat=1, opts={'serialize-keys': 1})

    def is_reloaded(k):
        # Check if a None was replaced (in d) with a non-empty thing
        if (df0[k] is None) and dot_lookup(d, k):
            return True
        # Check if is forced to be reloaded via its parent
        kp = k.split('.')[:-1]
        while kp:
            f = x0.get_field(kp)
            if not f.queryTaggedValue('allow-partial-update', True):
                return True
            kp.pop()
        return False

    for change, key, desc in dictdiffer.diff(df0, df2):
        if change == 'change':
            val0, val2 = desc
            assert val2 == df[key]
            assert val0 == df0[key]
            assert val2 == df2[key]
        elif change == 'add':
            for key2, val2 in desc:
                assert (val2 is None) or (key2 in df)
                assert df2[key2] == val2
        elif change == 'remove':
            for key0, val0 in desc:
                # A key may be removed in the following cases
                #  - by setting its update to None (df value)
                #  - an ancestor or self was fully reloaded
                assert ((key0 in df) and (df[key0] is None)) or is_reloaded(key0)
                assert df0[key0] == val0

    pass

@nose.tools.istest
def test_dictize():
    
    fixture_names = [
        'bbox1', 
        'contact1', 
        'foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6', 'foo7',
        'thesaurus_gemet_themes',
    ]
    
    for name in fixture_names:
        for test in _test_dictize(name):
            yield test

def _test_dictize_flattened(fixture_name, opts):

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
        assert (d[k] is None) or (k in expected_keys)

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
        'use-defaults': False,
    }

    x1 = factory().from_dict(d, is_flat=True, opts=opts1)
    d1 = x1.to_dict(flat=True, opts=opts)
    
    for change, key, desc in dictdiffer.diff(d, d1):
        if change in ['remove', 'add']:
            for k, v in desc:
                assert (v is None)
        else:
            assert False

def _test_dictize_nested(fixture_name, opts):

    x = getattr(fixtures, fixture_name)
    assert isinstance(x, Object)
    
    factory = type(x)
    
    # Dictize

    d = x.to_dict(flat=False, opts=opts)

    assert set(d.keys()) == set(x.get_fields(exclude_properties=1).keys())
    
    print
    print ' -- Dictize: nested opts=%r' %(opts)
    print d
    
    # Load
    
    opts1 = { 
        'unserialize-values': opts.get('serialize-values', False),
        'use-defaults': False,
    }

    x1 = factory().from_dict(d, is_flat=False, opts=opts1)
    d1 = x1.to_dict(flat=False, opts=opts)

    assert_equal(d, d1)

def _test_dictize(fixture_name):

    opts = {}
    yield _test_dictize_nested, fixture_name, opts
    yield _test_dictize_flattened, fixture_name, opts
    
    opts = { 'serialize-keys': True }
    yield _test_dictize_flattened, fixture_name, opts
    
    opts = { 'serialize-values': True }
    yield _test_dictize_nested, fixture_name, opts
    yield _test_dictize_flattened, fixture_name, opts
    
    opts = { 'serialize-values': 'json-s' }
    yield _test_dictize_nested, fixture_name, opts
    yield _test_dictize_flattened, fixture_name, opts
   
    opts = { 'serialize-keys': True, 'serialize-values': True }
    yield _test_dictize_flattened, fixture_name, opts
    
    opts = { 'serialize-keys': True, 'serialize-values': 'json-s' }
    yield _test_dictize_flattened, fixture_name, opts
    
    opts = { 'serialize-keys': True, 'key-prefix': 'test1', 'serialize-values': True }
    yield _test_dictize_flattened, fixture_name, opts
   
    for n in range(1, 5):
        opts = { 'max-depth': n }
        yield _test_dictize_flattened, fixture_name, opts
        opts = { 'serialize-keys': True, 'max-depth': n }
        yield _test_dictize_flattened, fixture_name, opts
        opts = { 'serialize-keys': True, 'key-prefix': 'test1', 'max-depth': n }
        yield _test_dictize_flattened, fixture_name, opts

#
# Fixture changesets
#

updates = {}

updates['foo'] = {
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

updates['inspire'] = {
    'upd-1': {
        'title': u"lala",
        'denominator': [u"asd"],
        'lineage': None,
        'access_constraints': [u"lololo1"]
    }, 
    'upd-2': {
        'bounding_box' : [{
                'nblat': 1.0,
                'sblat': 1.0,
                'wblng': 1.0,
                'eblng': 1.0,
            },],
        'temporal_extent' : [{ 
            'start': date(1999,1,1), 
            },]
    },
    'upd-3': {
        'keywords': [{
            'terms': ["agriculture", "climate"],
            'thesaurus': { 'name': 'keywords-gemet-concepts', }
        }],
    },
}

#
# Main 
#

if __name__ == '__main__':
    
    for t, x, y in test_dictize():
        t(x, y)

    _test_dictize_update('foo2', 'foo', 'upd-4')
    _test_dictize_update('inspire1', 'inspire', 'upd-3')
    _test_dictize_update_discard_junk('foo1', 'foo', 'upd-1')


