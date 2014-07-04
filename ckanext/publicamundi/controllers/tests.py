import datetime
import logging
import copy
import json

from pylons import url

from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object

log1 = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self, id=None):
        return u'Another test!'
    
    def get_field_markup(self):
        if request.method == 'POST':
            d = dict(request.params.items())
            response.headers['Content-Type'] = 'application/json' 
            return json.dumps(d)

        x = fixtures.foo1
        S = x.get_schema()
        test_fields = {
            'grade': { 'title': u'Foo Grade' },
            'rating': { 'title': u'Foo Rating' },
            'url': { 'title': u'Website URL' },
            'contacts': { 'title': u'Contacts', },
            'title': {
                'required': True,
                'classes': [ 'control-medium' ],
                'title': u'Title',
                'description': u'Blah blah',
                'placeholder': u'Enter a title',
                'attrs': { 'data-foo': 'baz' }
            },
            'temporal_extent': { 'title': u'Temporal Extent', },
            'reviewed': { 'title': u'Reviewed', },
            'notes': { 'description': u'Add a detailed description', },
            'thematic_category': {},
            'tags': {},
            'created': { 
                'title': u'Created At', 
                'placeholder': datetime.datetime.now(),
            },
            'wakeup_time': { 'title': u'Wakeup At',},
            'password': {},
        }
        c.form_sections = []
        for k, data in test_fields.items():
            f = x.get_field(k)
            c.form_sections.append({
                'heading': toolkit.literal('<h3>Field <code>%s</code></h3>' %(k)),
                'body': \
                    markup_for_field('edit', f, 'foo1', data) + \
                    toolkit.literal('<hr/>') + \
                    markup_for_field('read:bar', f, 'foo1', data)
            })
        #raise Exception('Break')
        c.form_class = 'form-horizontal' # 'form-horizontal'
        return render('tests/accordion-form.html')

    def get_field_markup_with_helper(self):
        x = fixtures.foo1
        k = 'title'
        return render('tests/field.html', extra_vars = {
            'field': x.get_field(k),
            'title': u'Title',
        })

    def get_object_markup(self):
        markup = ''
        c.form_sections = []
        # 1. A Point object
        obj = fixtures.pt1
        data = {
            'required': False,
            'classes': [],
            'input_classes': [ 'input-small' ],
            'title': u'Point A',
        }
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>Point</code></h3>'),
            'body': \
                markup_for_object('edit:baz', obj, 'pt1', data) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read:boz', obj, 'pt1', { 'title': u'Point B' })
        })
        # 2. A TemporalExtent object
        obj = fixtures.dt1
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>TemporalExtent</code></h3>'),
            'body': \
                markup_for_object('edit:faz.baz', obj, 'dt1', { 'title': u'Extent A' }) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read', obj, 'dt1', { 'title': u'Extent B' })
        })
        # 3. A PostalAddress object
        obj = PostalAddress(address=u'22 Acacia Avenue', postalcode=u'12345')
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>PostalAddress</code></h3>'),
            'body': \
                markup_for_object('edit:comfortable', obj, 'contact_info', { 'title': u'Address A' }) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read', obj, 'contact_info', { 'title': u'Address B' })
        })
        # Render
        c.form_class = 'form-horizontal'
        return render('tests/accordion-form.html')

    ## Sandbox

    def test1(self):
        c.form = None
        return render('tests/form.html')
        
