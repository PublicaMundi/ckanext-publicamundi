# -*- encoding: utf-8 -*-

import re
import datetime
import pytz
import isodate
import lxml.etree
import json
import itertools
import nose.tools
import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

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
        yield _test_field, fixture_name, k, f, v

def _test_field(fixture_name, k, f, v):
    '''Test XML serializion for an arbitrary field
    ''' 
    
    ser = xml_serializer_for_field(f)
    assert ser 
    ser.target_namespace = 'http://example.com/test-field'
    verifyObject(IXmlSerializer, ser)
    
    xsd = ser.to_xsd(wrap_into_schema=True)
    print 'XML schema: -' 
    lxml.etree.dump(xsd)

    e1 = ser.to_xml(v)
    print 'XML dump (to_xml): - '
    lxml.etree.dump(e1)
    
    s1 = ser.dumps(v)
    print 'XML dump (dumps): - '
    print s1

    v1 = ser.loads(s1)
    assert unicode(v1) == unicode(v)

def _test_fixture_object(fixture_name):
    '''Test XML serializion for an arbitrary fixture object.
    '''
    
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

def test_field_nativestring():

    f = zope.schema.NativeString(
        title = u'Code',
        required = False,
        min_length = 8,
        max_length = 8)
    v = 'AA123456'
    f.validate(v)

    yield _test_field, '-', 'code', f, v

def test_field_bool():
    
    f = zope.schema.Bool(
        title = u'Reviewed',
        description = u'The text is reviewed',
        required = True)

    v = True
    f.validate(v)
    
    yield _test_field, '-', 'reviewed', f, v

def test_field_float():
    
    f = zope.schema.Float(
        title = u'Price',
        min = .0,
        description = u'The price of something',
        required = True)

    v = 5.78
    f.validate(v)
    
    yield _test_field, '-', 'price', f, v

def test_field_integer():
    
    f = zope.schema.Int(
        title = u'Grade',
        description = u'The exams grade',
        min = 0, 
        max = 20,
        required = True)

    v = 19
    f.validate(v)

    yield _test_field, '-', 'grade', f, v
    
    f = zope.schema.Int(
        title = u'Height',
        description = u'The mountain height',
        min = 0, 
        required = True)

    v = 1503
    f.validate(v)

    yield _test_field, '-', 'height', f, v

def test_field_choice():
    
    f = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('environment', 'environment', u'Environment'),
            SimpleTerm('government', 'government', u'Government'),
            SimpleTerm('health', 'health', u'Health'),
            SimpleTerm('economy', 'economy', u'Economy'))),
        title = u'Thematic category',
        required = True,
        default = 'economy')

    v = 'health'
    f.validate(v)

    yield _test_field, '-', 'thematic_category', f, v

def test_field_textline():

    f = zope.schema.Text(
        title = u'Author Notes',
        required = False,
        min_length = 12)
    v = u'Αυτο ειναι μια σημειωση'
    f.validate(v)

    yield _test_field, '-', 'notes', f, v

    f = zope.schema.TextLine(
        title = u'Summary',
        description = u'A summary of a chapter',
        required = True,
        min_length = 6, 
        max_length = 128)
    v = u'This is a Hello-World example'
    f = f.bind(FieldContext(key='summary', value=v))
    f.validate(v)

    yield _test_field, '-', 'summary', f, v
    
    f = zope.schema.TextLine(
        title = u'Postal Code',
        required = False,
        constraint = re.compile('^[a-z][0-9]{5,5}$', re.IGNORECASE).match)
    v = u'A12345'
    f = f.bind(FieldContext(key='postal_code', value=v))
    f.validate(v)

    yield _test_field, '-', 'postalcode', f, v

def test_field_datetime():
    
    f = zope.schema.Datetime(
        title = u'Created',
        description = u'A timestamp for creation',
        required = True,
        min = datetime.datetime(2012, 1, 1))

    v = datetime.datetime(2014, 8, 1, 8, 0, 0)
    f.validate(v)
    
    yield _test_field, '-', 'created_at', f, v

    f = zope.schema.Datetime(
        title = u'Created',
        description = u'A timestamp (with timezone info) for creation',
        required = True)

    v = datetime.datetime(2014, 8, 1, 8, 0, 0, tzinfo=pytz.timezone('Europe/Athens'))
    f.validate(v)
    
    yield _test_field, '-', 'created_at', f, v

def test_field_date():
    
    f = zope.schema.Date(
        title = u'Created',
        description = u'A datestamp for creation',
        required = True,
        min = datetime.date(2012, 1, 1),
        max = datetime.date(2014, 1, 1))

    v = datetime.date(2013, 8, 1)
    f.validate(v)
    
    yield _test_field, '-', 'created_at', f, v

def test_field_time():
    
    f = zope.schema.Time(
        title = u'Wakeup Time',
        description = u'The wakeup time',
        required = True,
        min = datetime.time(6, 0, 0),
        max = datetime.time(8, 30, 0))

    v = datetime.time(7, 20, 0)
    f.validate(v)
    
    yield _test_field, '-', 'wakeup_time', f, v

def test_field_list_of_textline():
    
    class IX(zope.interface.Interface):
    
        gemet_keywords = zope.schema.List(
            title = u'Keywords',
            description = u'A collection of keywords',
            required = True,
            value_type = zope.schema.TextLine(
                #title = u'Keyword'
            ),
            min_length = 1,
            max_length = 12)
    
        gemet_keywords.value_type.setTaggedValue('name', 'tag')
   
    f = zope.schema.List(
        title = u'Keywords',
        description = u'A collection of keywords',
        required = True,
        value_type = zope.schema.TextLine(
            title = u'Keyword'
        ),
        min_length = 1,
        max_length = 12)
    f.value_type.setTaggedValue('name', 'tag')

    v = [u'alpha', u'beta', u'gamma']
    f.validate(v)
    
    yield _test_field, '-', 'keywords', f, v

    f = IX.get('gemet_keywords') 
    v = [u'alpha', u'beta', u'gamma']
    f.validate(v)

    yield _test_field, '-', 'gemet_keywords', f, v

if __name__ == '__main__':
    print ' -- '
    for tester, name, k, f, v in test_field_list_of_textline():
        tester(name, k, f, v)
    #for tester, name, k, f, v in test_fields():
    #    tester(name, k, f, v)
    #for tester, name in test_objects():
    #    tester(name)
