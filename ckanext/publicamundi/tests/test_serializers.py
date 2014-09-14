# -*- encoding: utf-8 -*-

import datetime
import json
import itertools
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib.metadata import ISerializer
from ckanext.publicamundi.lib.metadata.types import Foo
from ckanext.publicamundi.lib.metadata import serializers
from ckanext.publicamundi.lib.metadata.serializers import \
    serializer_for_key_tuple, serializer_for_field
from ckanext.publicamundi.lib.metadata.base import serializer_for_object
from ckanext.publicamundi.tests import fixtures

def test_objects():
    yield _test_fixture_object, 'foo1'    
    yield _test_fixture_object, 'thesaurus_gemet_concepts'    

def test_fields():
    '''Return tuples of (tester, key, field, val) to be tested 
    '''
    
    it = itertools.chain(
        _test_fixture_fields('foo1'),
        _test_fixture_fields('thesaurus_gemet_concepts')
    )

    for p in it:
        yield p

def test_key_tuples():
    '''Test key-tuple serializer'''  
    
    x = fixtures.foo1
    
    ser = serializer_for_key_tuple()
    for kt, field in x.get_flattened_fields().items():
        kt1 = tuple(map(str, kt))
        k = ser.dumps(kt1)
        assert ser.loads(k) == kt1
    
    ser = serializer_for_key_tuple()
    ser.prefix = 'boo'
    for kt, field in x.get_flattened_fields().items():
        kt1 = tuple(map(str, kt))
        k = ser.dumps(kt1)
        assert ser.loads(k) == kt1

def _test_fixture_fields(fixture_name):
    x = getattr(fixtures, fixture_name)
    d = x.to_dict(flat=True)
    fields = x.get_flattened_fields()
    for k, v in d.items():
        f = fields[k]
        yield _test_leaf_field, fixture_name, k, f, v

def _test_leaf_field(fixture_name, k, f, v):
    
    ser = serializer_for_field(f)
    assert ser
    verifyObject(ISerializer, ser)

    s1 = ser.dumps(v)
    v1 = ser.loads(s1)
    assert v1 == v

def _test_fixture_object(fixture_name):
    x = getattr(fixtures, fixture_name)
    ser = serializer_for_object(x)
    assert ser
    verifyObject(ISerializer, ser)

    s = ser.dumps(x)
    assert s

    x1 = ser.loads(s)
    assert x1

    d = x.to_dict(flat=True)
    d1 = x1.to_dict(flat=True)
    
    keys = set(d.keys())
    keys1 = set(d1.keys())

    assert keys == keys1

    for k in keys:
        assert d[k] == d1[k] 

def test_field_textline():
    f = zope.schema.TextLine(title=u'Summary')
    
    for fmt in ['default']:
        ser = serializer_for_field(f, fmt=fmt)
        assert ser 
        verifyObject(ISerializer, ser)

        v = u'Καλημέρα Κόσμε'
        s = ser.dumps(v)
        assert s    

        v1 = ser.loads(s)
        assert v == v1
  
    fmt = 'not-existing-format'
    try:
        ser = serializer_for_field(f, fmt=fmt)
    except:
        pass
    else:
        assert False, 'Unexpected serialization format'

def test_field_datetime():
    f = zope.schema.Datetime(title=u'Created')
    
    ser = serializer_for_field(f)
    assert ser 
    verifyObject(ISerializer, ser)

    dt1 = datetime.datetime(2014, 8, 1, 8, 0, 0)

    s = ser.dumps(dt1)
    print s
    assert s == '2014-08-01T08:00:00'   

    v = ser.loads(s)
    assert v == dt1

if __name__ == '__main__':
    test_field_textline()
    test_field_datetime()
    for tester, name, k, f, v in test_fields():
        tester(name, k, f, v)
    for tester, name in test_objects():
        tester(name)
