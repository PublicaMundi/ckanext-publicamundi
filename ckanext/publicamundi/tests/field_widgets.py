import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import get_markup_for_field

from ckanext.publicamundi.tests.fixtures import x1

def test_read_markup_for_field(x, k, prefix):
    S = x.get_schema()
    F = S.get(k)
    f = F.get(x)
    return get_markup_for_field('read', F, f, prefix)

def test_edit_markup_for_field(x, k, prefix):
    S = x.get_schema()
    F = S.get(k)
    f = F.get(x)
    return get_markup_for_field('edit', F, f, prefix)
