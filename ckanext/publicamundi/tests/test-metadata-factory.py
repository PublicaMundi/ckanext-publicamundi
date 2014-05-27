import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata import BaseObject
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.schemata import *

from ckanext.publicamundi.tests.fixtures import x1

errs = x1.validate()
assert not errs
d1r = x1.to_dict(flat=False)
d1f = x1.to_dict(flat=True)

s1r = x1.to_json(flat=False)
s1f = x1.to_json(flat=True)

factory = BaseObject.Factory(IInspireMetadata)

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


