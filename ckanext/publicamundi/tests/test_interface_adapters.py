import zope.interface
import zope.interface.verify
import itertools

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import *

class Foo1(Object):
    
    zope.interface.implements(IFooMetadata)

class Foo2(Object):
    pass

zope.interface.classImplements(Foo2, IFooMetadata)

Foo3 = type('Foo3', (Object,), {})

zope.interface.classImplements(Foo3, IFooMetadata)

# Tests 

def test_adapter_registry():
    info1 = adapter_registry.queryMultiAdapter([], IContactInfo)
    assert info1
    assert zope.interface.verify.verifyObject(IContactInfo, info1)

    pt1 = adapter_registry.queryMultiAdapter([], IPoint)
    assert pt1
    assert zope.interface.verify.verifyObject(IPoint, pt1)

    cls = adapter_registry.lookup([], IContactInfo)
    assert cls
    assert zope.interface.verify.verifyClass(IContactInfo, cls)

def _test_field_factory(cls_name, k):
    cls = globals().get(cls_name)
    factory = cls.get_field_factory(k, None)
    if factory:
        assert callable(factory)
        f = factory()
        assert not (f is None)

def test_field_factories():
    for X in [FooMetadata, Foo1, Foo2, Foo3]:
        S = X.get_schema()
        for k in zope.schema.getFieldNames(S):
            yield _test_field_factory, X.__name__, k

