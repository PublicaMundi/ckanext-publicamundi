import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_field

from ckanext.publicamundi.tests.fixtures import x1

def get_read_markup_for_field(x, k, prefix):
    S = x.get_schema()
    F = S.get(k)
    f = F.get(x)
    return generate_markup_for_field('read', F, f, prefix)

def get_edit_markup_for_field(x, k, prefix):
    S = x.get_schema()
    F = S.get(k)
    f = F.get(x)
    return generate_markup_for_field('edit', F, f, prefix)


def test_read_markup_for_text_field():
    return get_read_markup_for_field(x1, 'title', 'x1')

def test_edit_markup_for_text_field():
    return get_edit_markup_for_field(x1, 'title', 'x1')

