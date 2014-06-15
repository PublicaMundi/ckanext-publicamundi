import zope.interface

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import *

info1 = adapter_registry.queryMultiAdapter([], IContactInfo)

pt1 = adapter_registry.queryMultiAdapter([], IPoint)

cls = adapter_registry.lookup([], IContactInfo)

class X1(BaseObject):
    zope.interface.implements(IInspireMetadata)

X2 = InspireMetadata

for X in [X1, X2]:
    print ' == Field factories for %s == ' %(X)
    S = X.get_schema()
    for k in zope.schema.getFieldNames(S):
        factory = X.get_field_factory(k)
        print k, ':', factory

