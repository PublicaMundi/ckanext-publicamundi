import zope.interface
import zope.schema
import json
import datadiff
from datadiff.tools import assert_equal
from datetime import date, time, datetime
from itertools import chain


from ckanext.publicamundi.lib.metadata.base import \
    Object, serializer_for_object, \
    serializer_for_field, serializer_for_key_tuple
from ckanext.publicamundi.tests import fixtures

leaf_types = (basestring, bool, int, long, float,)

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

    d = x.to_dict(flat=True, opts=opts)

    print
    print ' -- Dictize: flattened opts=%r' %(opts)
    print d

    key_type = basestring if opts.get('serialize-keys') else tuple
    key_prefix = opts.get('key-prefix')
    
    expected_keys = x.get_flattened_fields().keys()
    if key_type is basestring:
        kser = serializer_for_key_tuple()
        kser.prefix = key_prefix
        expected_keys = map(kser.dumps, expected_keys)

    for k in d:
        assert isinstance(k, key_type)
        assert k in expected_keys

    if key_prefix:
        for k in d:
            assert k.startswith(key_prefix)

    if opts.get('serialize-values'):
        for v in d.itervalues():
            assert v is None or isinstance(v, leaf_types)

    opts1 = { 
        'unserialize-keys': opts.get('serialize-keys', False),
        'unserialize-values': opts.get('serialize-values', False),
        'key-prefix': opts.get('key-prefix', None),
    }

    x1 = factory().from_dict(d, is_flat=True, opts=opts1)
    d1 = x1.to_dict(flat=True, opts=opts)
    
    assert_equal(d, d1)

def _test_nested_dict(fixture_name, opts):

    x = getattr(fixtures, fixture_name)
    assert isinstance(x, Object)
    
    factory = type(x)

    d = x.to_dict(flat=False, opts=opts)

    assert set(d.keys()) == set(x.get_field_names())
    
    print
    print ' -- Dictize: nested opts=%r' %(opts)
    print d
    
    opts1 = { 
        'unserialize-values': opts.get('serialize-values', False),
    }

    x1 = factory().from_dict(d, is_flat=False, opts=opts1)
    d1 = x1.to_dict(flat=False, opts=opts)

    assert_equal(d, d1)

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
   
if __name__ == '__main__':
    for t, x, y in test_objects():
        t(x, y)
