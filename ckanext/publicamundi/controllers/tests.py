import logging
import json

from pylons import url

from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_object

log1 = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self, id=None):
        return u'Another test!'

    def test_field_markup(self):
        k = 'title'
        x = fixtures.foo1
        S = x.get_schema()
        F = S.get(k)
        f = F.get(x)
        data = {
            'required': True,
            'classes': [ 'control-medium' ],
            'title': u'Foo',
            'placeholder': u'Enter a title',
        }
        c.data = markup = generate_markup_for_field('edit', F, f, 'foo1', **data)
        return render('tests/page.html')

    def test_field_markup_with_helper(self):
        k = 'title'
        x = fixtures.foo1
        S = x.get_schema()
        F = S.get(k)
        f = F.get(x)
        return render('tests/field.html', extra_vars = {
            'field_def': F,
            'field_val': f,
            'title': u'Title',
        })

    def test_object_markup(self):
        obj = fixtures.pt1
        data = {
            'required': False,
            'classes': [],
            'input_classes': [ 'input-small' ],
            'title': u'Point A',
        }
        c.data = markup = generate_markup_for_object('edit', obj, 'pt1', **data)
        return render('tests/page.html')

