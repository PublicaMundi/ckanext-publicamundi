import datetime
import json
import itertools
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib.metadata import ISerializer, serializer_for_object
from ckanext.publicamundi.lib.metadata.types import Foo
from ckanext.publicamundi.lib.metadata.serializers import *
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
    
    ser = serializer_for_field(f)
    assert ser 
    verifyObject(ISerializer, ser)

    s = ser.dumps(u'Hello World')
    assert s    

    v = ser.loads(s)
    assert v == u'Hello World'

def test_field_datetime():
    f = zope.schema.Datetime(title=u'Created')
    
    ser = serializer_for_field(f)
    assert ser 
    verifyObject(ISerializer, ser)

    dt1 = datetime.datetime(2014, 8, 1, 8, 0, 0)

    s = ser.dumps(dt1)
    print s
    assert s == '2014-08-01 08:00:00'   

    v = ser.loads(s)
    assert v == dt1

if __name__ == '__main__':
    test_field_textline()
    test_field_datetime()
    for tester, name, k, f, v in test_fields():
        tester(name, k, f, v)
    for tester, name in test_objects():
        tester(name)
