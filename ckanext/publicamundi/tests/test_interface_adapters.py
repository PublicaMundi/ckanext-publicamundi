import zope.interface
import zope.interface.verify
import itertools

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import *

class InspireMetadata1(BaseObject):
    zope.interface.implements(IInspireMetadata)

## Tests ##

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
    factory = cls.get_field_factory(k)
    if not (factory is None):
        assert callable(factory)
        f = factory()
        assert not (f is None)

def test_field_factories():
    for X in [InspireMetadata, InspireMetadata1]:
        S = X.get_schema()
        for k in zope.schema.getFieldNames(S):
            yield _test_field_factory, X.__name__, k

