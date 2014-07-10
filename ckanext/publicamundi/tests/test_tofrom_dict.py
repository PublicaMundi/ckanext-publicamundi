import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.tests import fixtures

def test_objects():
    
    yield _test_dictization, 'contact1'
    yield _test_dictization, 'foo1'

def _test_dictization(fixture_name):

    from datetime import date, time, datetime

    x1 = getattr(fixtures, fixture_name)
    assert isinstance(x1, Object)

    d1f = x1.to_dict(flat=True)
    for k in d1f: 
        assert isinstance(k, tuple)
    print
    print ' -- flat --'
    print d1f

    d1f1 = x1.to_dict(flat=True, opts={ 'serialize-keys': True })
    for k in d1f1: 
        assert isinstance(k, basestring)
    print
    print ' -- flat, serialize-keys  --'
    print d1f1
    
    d1f2 = x1.to_dict(flat=True, opts={ 'serialize-values': True })
    for k in d1f2: 
        assert isinstance(k, tuple)
    print
    print ' -- flat, serialize-values  --'
    print d1f2
   
    d1f3 = x1.to_dict(flat=True, opts={ 'serialize-keys': True, 'serialize-values': True })
    for k, v in d1f3.items(): 
        assert isinstance(k, basestring)
        assert isinstance(v, basestring) or isinstance(v, int) or isinstance(v, float) or \
            isinstance(v, date) or isinstance(v, time) or isinstance(v, datetime)
    print
    print ' -- flat, serialize-keys, serialize-values  --'
    print d1f3

    d1r = x1.to_dict(flat=False)
    assert (set(d1r.keys()) == set(x1.get_field_names()))
    for k in d1r:
        assert isinstance(k, basestring)
    print
    print ' -- nested --'
    print d1r
        
    d1r1 = x1.to_dict(flat=False, opts={ 'serialize-values': True })
    assert (set(d1r1.keys()) == set(x1.get_field_names()))
    for k in d1r1:
        assert isinstance(k, basestring)
    print
    print ' -- nested, serialize-values --'
    print d1r1

if __name__ == '__main__':
    for t,x in test_objects():
        t(x)
