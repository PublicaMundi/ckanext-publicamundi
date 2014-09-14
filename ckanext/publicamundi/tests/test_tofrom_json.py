import zope.interface
import zope.schema
import json

from ckanext.publicamundi.tests import fixtures

def test_objects():
    for name in ['contact1', 'bbox1', 'foo1']:
        yield _test_fixture_object, name

def _test_fixture_object(name):
    '''Convert a valid object to/from JSON
    '''
    
    x1 = getattr(fixtures, name)
    assert x1
    
    factory = type(x1)

    s1d = x1.to_json(flat=False, indent=4)
    s1f = x1.to_json(flat=True, indent=4)

    # Test nested JSON objects

    x2 = factory()
    x2.from_json(s1d, is_flat=False)
    errs2 = x2.validate()
    assert not errs2
    s2d = x2.to_json(flat=False, indent=4)
    s2f = x2.to_json(flat=True, indent=4)
    assert s1d == s2d
    assert s1f == s2f

    # Test flattened JSON objects

    x3 = factory()
    x3.from_json(s1f, is_flat=True)
    errs3 = x3.validate()
    assert not errs3
    s3d = x3.to_json(flat=False, indent=4)
    s3f = x3.to_json(flat=True, indent=4)
    assert s1d == s3d
    assert s1f == s3f

if __name__ == '__main__':
    _test_fixture_object('foo1')

