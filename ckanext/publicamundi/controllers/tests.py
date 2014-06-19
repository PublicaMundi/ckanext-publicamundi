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

    def get_field_markup(self):
        x = fixtures.foo1
        S = x.get_schema()
        test_fields = {
            'title': {
                'required': True,
                'classes': [ 'control-medium' ],
                'title': u'Title',
                'placeholder': u'Enter a title',
                'attrs': { 'data-foo': 'baz' }
            },
            'reviewed': {
                'title': u'Reviewed',
            },
            'notes': {
                'description': u'Add a detailed description',
            },
            'thematic_category': {
            }
        }
        markup = ''
        for k, data in test_fields.items():
            F = S.get(k)
            f = F.get(x)
            markup += toolkit.literal('<h3>Edit markup for field <code>%s</code></h3>' %(k))
            markup += generate_markup_for_field('edit.baz', F, f, 'foo1', **data)
            markup += toolkit.literal('<h3>Read markup for field <code>%s</code></h3>' %(k))
            markup += generate_markup_for_field('read.bar', F, f, 'foo1', **data)
        #raise Exception('Break')
        c.form = markup
        return render('tests/form.html')

    def get_field_markup_with_helper(self):
        x = fixtures.foo1
        k = 'title'
        S = x.get_schema()
        F = S.get(k)
        f = F.get(x)
        return render('tests/field.html', extra_vars = {
            'field_def': F,
            'field_val': f,
            'title': u'Title',
        })

    def get_object_markup(self):
        markup = ''
        # A Point object
        obj = fixtures.pt1
        data = {
            'required': False,
            'classes': [],
            'input_classes': [ 'input-small' ],
            'title': u'Point A',
        }
        markup += toolkit.literal('<h3>Markup for object <code>Point</code></h3>')
        markup += generate_markup_for_object('edit.baz', obj, 'pt1', **data)
        # A TemporalExtent object
        obj = fixtures.dt1
        data = {}
        markup += toolkit.literal('<h3>Markup for object <code>TemporalExtent</code></h3>')
        markup += generate_markup_for_object('edit.faz', obj, 'dt1', **data)
        # Render 
        c.form = markup
        return render('tests/form.html')

