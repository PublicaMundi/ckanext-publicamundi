import re
import datetime
import lxml.etree
import json
import itertools
import nose.tools
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib.metadata import *
from ckanext.publicamundi.lib.metadata.serializers import *
from ckanext.publicamundi.lib.metadata.xml_serializers import *
from ckanext.publicamundi.tests import fixtures

@nose.tools.nottest
def test_objects():
    yield _test_fixture_object, 'foo1'    
    yield _test_fixture_object, 'thesaurus_gemet_concepts'    

@nose.tools.nottest
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
        f = fields[k].bind(FieldContext(key=k.join('-'), value=v))
        yield _test_leaf_field, fixture_name, k, f, v

def _test_leaf_field(fixture_name, k, f, v):
    
    ser = xml_serializer_for_field(f)
    assert ser 
    verifyObject(IXmlSerializer, ser)
    
    xsd = ser.to_xsd()
    print 'XML schema: -' 
    lxml.etree.dump(xsd)

    e1 = ser.to_xml(v)
    print 'XML dump (to_xml): - '
    lxml.etree.dump(e1)
    
    s1 = ser.dumps(v)
    print 'XML dump (dumps): - '
    print s1

    v1 = ser.loads(s1)
    assert v1 == v

def _test_fixture_object(fixture_name):
    x = getattr(fixtures, fixture_name)
    # Fixme xml_serializer_for_object
    ser = serializer_for_object(x) 
    assert ser 
    verifyObject(IXmlSerializer, ser)

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

    f = zope.schema.Text(
        title=u'Author Notes',
        min_length=12)
    v = u'Blaah\nBlaaah'
    f.validate(v)

    yield _test_leaf_field, '-', 'notes', f, v

    f = zope.schema.TextLine(
        title = u'Summary', 
        min_length = 6, 
        max_length = 128)
    v = u'This is a Hello-World example'
    f = f.bind(FieldContext(key='summary', value=v))
    f.validate(v)

    yield _test_leaf_field, '-', 'summary', f, v
    
    f = zope.schema.TextLine(
        title = u'Postal Code', 
        constraint = re.compile('^[a-z][0-9]{5,5}$', re.IGNORECASE).match)
    v = u'A12345'
    f = f.bind(FieldContext(key='postal_code', value=v))
    f.validate(v)

    yield _test_leaf_field, '-', 'postalcode', f, v

@nose.tools.nottest
def test_field_datetime():
    f = zope.schema.Datetime(title=u'Created')
    v = datetime.datetime(2014, 8, 1, 8, 0, 0)
    f = f.bind(FieldContext(key='created_at', value=v))
    f.validate(v)
    
    yield _test_leaf_field, '-', 'created_at', f, v

if __name__ == '__main__':
    print ' -- '
    for tester, name, k, f, v in test_field_textline():
        tester(name, k, f, v)
    print ' -- '
    #for tester, name, k, f, v in test_field_datetime():
    #    tester(name, k, f, v)
    #print ' -- '
    #test_field_datetime()
    #for tester, name, k, f, v in test_fields():
    #    tester(name, k, f, v)
    #for tester, name in test_objects():
    #    tester(name)
