import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata import Object
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.tests import fixtures

def test_tofrom_dicts():
    x1 = fixtures.foo1

    errs = x1.validate()
    assert not errs
    d1r = x1.to_dict(flat=False)
    d1f = x1.to_dict(flat=True)

    s1r = x1.to_json(flat=False)
    s1f = x1.to_json(flat=True)

    factory = Object.Factory(schemata.IFoo)

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
        "notes": u"Hello World",
        "wakeup_time": u"08:00:00"
    }
     
    factory = Object.Factory(schemata.IFoo, opts={
        'unserialize-keys': True,
        'unserialize-values': True,
    })

    obj = factory(d, is_flat=True)
    
    errors = obj.validate()
    errors = obj.dictize_errors(errors)

    assert not errors

if __name__ == '__main__':
    test_tofrom_dicts()
    test_from_serialized()

