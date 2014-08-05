import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
import datetime
import json
import itertools

from ckanext.publicamundi.lib.metadata.types import Foo
from ckanext.publicamundi.lib.metadata.serializers import *
from ckanext.publicamundi.tests import fixtures

def test_fixtures():
    '''Return tuples of (tester, key, field, val) to be tested 
    '''
    
    it = itertools.chain(
        _test_fixture('foo1'),
        _test_fixture('thesaurus_gemet_concepts')
    )

    for p in it:
        yield p

def _test_fixture(fixture_name):
    x = getattr(fixtures, fixture_name)
    d = x.to_dict(flat=True)
    fields = x.get_flattened_fields()
    for k, v in d.items():
        f = fields[k]
        yield _test_leaf_field, fixture_name, k, f, v

def _test_leaf_field(fixture_name, k, f, v):
    
    ser = serializer_for_field(f)
    assert ser

    s1 = ser.dumps(v)
    v1 = ser.loads(s1)
    assert v1 == v

def test_field_textline():
    f = zope.schema.TextLine(title=u'Summary')
    
    ser = serializer_for_field(f)
    assert ser 

    s = ser.dumps(u'Hello World')
    assert s    

    v = ser.loads(s)
    assert v == u'Hello World'

def test_field_datetime():
    f = zope.schema.Datetime(title=u'Created')
    
    ser = serializer_for_field(f)
    assert ser 

    dt1 = datetime.datetime(2014, 8, 1, 8, 0, 0)

    s = ser.dumps(dt1)
    print s
    assert s == '2014-08-01 08:00:00'   

    v = ser.loads(s)
    assert v == dt1

if __name__ == '__main__':
    test_field_textline()
    test_field_datetime()
    for tester, name, k, f, v in test_fixtures():
        tester(name, k, f, v)

