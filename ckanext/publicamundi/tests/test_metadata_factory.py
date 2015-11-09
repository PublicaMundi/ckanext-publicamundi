import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
import json

from ckanext.publicamundi.lib.metadata import (
    Object, get_object_factory, object_null_adapter)
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.tests import fixtures

#
# Prepare a named null adapter 
#

class Baz(object):

    def __call__(self):
        return u'Baobab'

baz_factory = Baz()

@object_null_adapter(name='another-foo')
class AnotherFoo(types.Metadata):
    
    zope.interface.implements(schemata.IFooMetadata)
    
    title = None
    baz = baz_factory
    temporal_extent = None
    contact_info = types.ContactInfo
    grade = None

#
# Tests
#

def test_factories():

    fc1 = get_object_factory(schemata.IFooMetadata)
    o1 = fc1()
    verifyObject(schemata.IFooMetadata, o1)
    assert isinstance(o1, types.FooMetadata)
    
    fc2 = get_object_factory(schemata.IFooMetadata, name='another-foo')
    o2 = fc2()
    verifyObject(schemata.IFooMetadata, o2)
    assert isinstance(o2, AnotherFoo)
    assert (
        o2.baz == u'Baobab' and 
        o2.temporal_extent is None and
        isinstance(o2.contact_info, types.ContactInfo))
    
    try:
        fc3 = get_object_factory(schemata.IFooMetadata, name='a-non-existing-name')
    except (ValueError, LookupError) as ex:
        pass
    else:
        assert False, 'This should have failed'

def test_tofrom_dicts():

    yield _test_tofrom_dicts, 'bbox1', schemata.IGeographicBoundingBox 
    yield _test_tofrom_dicts, 'foo1', schemata.IFooMetadata
    yield _test_tofrom_dicts, 'foo2', schemata.IFooMetadata
    yield _test_tofrom_dicts, 'foo3', schemata.IFooMetadata

def _test_tofrom_dicts(fixture_name, schema):
    
    x1 = getattr(fixtures, fixture_name)
    verifyObject(schema, x1)
    
    d1r = x1.to_dict(flat=False)
    d1f = x1.to_dict(flat=True)

    s1r = x1.to_json(flat=False)
    s1f = x1.to_json(flat=True)

    factory = Object.Factory(schema)

    x2 = factory.from_dict(d1r, is_flat=False)
    x3 = factory.from_dict(d1f, is_flat=True)

    s2r = x2.to_json(flat=False)
    s2f = x2.to_json(flat=True)
    assert s2r == s1r
    assert s2f == s1f

    s3r = x3.to_json(flat=False)
    s3f = x3.to_json(flat=True)
    assert s3r == s1r
    assert s3f == s1f

def test_from_serialized():
    
    d = {
        "tags.2": u"gamma",
        "tags.1": u"beta",
        "tags.0": u"alpha",
        "tags-joined": u"alpha,beta,gamma",
        "rating": u"0",
        "grade": u"13.7",
        "contacts.personal.email": u"nobody@example.com",
        "contacts.office.address.address": u"South Pole",
        "title": u"Ababoua Ababoua",
        "submit": u"Submit Query",
        "contact_info.address.postalcode": u'12345',
        "contacts.office.address.postalcode": u"12345",
        "contact_info.email": u"nomad@somewhere.com",
        "temporal_extent.start": u"2014-05-27",
        "temporal_extent.end": u"2014-05-29",
        "contacts.office.email": None,
        "contacts.personal.address.postalcode": u"54321",
        "created": u"2014-06-11 00:00:00",
        "url": "http://example.com",
        "baz": u"Bazzz",
        "thematic_category": u"economy",
        "contact_info.address.address": u'Nowhere Land',
        "contacts.personal.address.address": u"North Pole",
        "description": u"Hello World",
        "wakeup_time": u"08:00:00",
        "created": "1997-09-01T00:00:00",
    }
     
    factory = Object.Factory(schemata.IFooMetadata, opts={
        'unserialize-keys': True,
        'unserialize-values': True,
    })

    obj = factory(d, is_flat=True)
    
    errors = obj.validate()
    errors = obj.dictize_errors(errors)

    assert not errors

if __name__ == '__main__':
    
    test_factories()

    _test_tofrom_dicts('foo1', schemata.IFooMetadata)
    
    test_from_serialized()

