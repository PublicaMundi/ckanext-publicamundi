import zope.interface
import zope.schema
from zope.interface.verify import verifyObject
import json

from ckanext.publicamundi.lib.json_encoder import JsonEncoder
from ckanext.publicamundi.lib.metadata import Object
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.tests import fixtures

def print_as_dict(obj):
    assert isinstance(obj, Object)

    d1 = obj.to_dict(flat=False)
    print d1 #json.dumps(d1, indent=4)

    d2 = obj.to_dict(flat=True)
    for k in sorted(d2):
        print k, ':', d2[k]

def validate(x):
    obj = getattr(fixtures, x)
    errors = obj.validate()
    if not errors:
        print_as_dict(obj)

def convert_to_dict(x):
    obj = getattr(fixtures, x)

    d = obj.to_dict()
    obj1 = types.InspireMetadata().from_dict(d)
    s = json.dumps(d, cls=JsonEncoder)
    s1 = json.dumps(obj1.to_dict(), cls=JsonEncoder)
    assert s == s1

    d = obj.to_dict(flat=True)
    obj2 = types.InspireMetadata().from_dict(d, is_flat=True)
    s = json.dumps(obj.to_dict(), cls=JsonEncoder)
    s2 = json.dumps(obj2.to_dict(), cls=JsonEncoder)
    assert s == s2

def test_validators():
    yield validate, 'x1'

def test_dict_converters():
    yield convert_to_dict, 'x1'

if __name__  == '__main__':
    validate('x1')
    convert_to_dict('x1')

