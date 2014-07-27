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

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.types import Object
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object

from ckanext.publicamundi.tests import fixtures

log1 = logging.getLogger(__name__)

class TestsController(BaseController):

    def index(self, id=None):
        return u'Another test!'
    
    def get_fields_markup(self):
        if request.method == 'POST':
            d = dict(request.params.items())
            response.headers['Content-Type'] = 'application/json' 
            return json.dumps(d)

        x = fixtures.foo1
        S = x.get_schema()
        test_fields = {
            'url': { 'title': u'Website URL' },
            'rating': { 'title': u'Foo Rating' },
            'grade': { 'title': u'Foo Grade' },
            'contacts': { 'title': u'Contacts', },
            'title': {
                'required': True,
                'classes': [ 'control-medium' ],
                'title': u'Title',
                'description': u'Blah blah',
                'placeholder': u'Enter a title',
                'attrs': { 'data-foo': 'baz', 'data-boo': 'faz', 'autocomplete': 'off' }
            },
            'temporal_extent': { 'title': u'Temporal Extent', },
            'reviewed': { 'title': u'Reviewed', },
            'notes': { 'description': u'Add a detailed description', },
            'thematic_category': {},
            'tags': {},
            'created': { 'title': u'Created At', 'placeholder': datetime.datetime.now() },
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

    def get_objects_markup(self):
        markup = ''
        c.form_sections = []
        
        # 1. A Point object
        obj = fixtures.pt1
        assert isinstance(obj, types.Point)
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
        assert isinstance(obj, types.TemporalExtent)
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>TemporalExtent</code></h3>'),
            'body': \
                markup_for_object('edit:faz.baz', obj, 'dt1', { 'title': u'Extent A' }) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read', obj, 'dt1', { 'title': u'Extent B' })
        })
        
        # 3. A PostalAddress object
        obj = types.PostalAddress(address=u'22 Acacia Avenue', postalcode=u'12345')
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

    def edit_foo(self, id='foo1'):
        obj = getattr(fixtures, id)
        assert isinstance(obj, types.Foo)
        if request.method == 'POST':
            d = dict(request.params.items())
            factory = Object.Factory(schemata.IFoo)
            o = factory().from_dict(d, is_flat=True, opts={
                'unserialize-keys': True,
                'unserialize-values': True,
            })
            response.headers['Content-Type'] = 'application/json' 
            return o.to_json()
        else:
            c.form_class = 'form-horizontal'
            c.form_markup = markup_for_object('edit', obj, name_prefix='', data={ 
                'title': u'Foo #1' 
            })
            return render('tests/form.html')

    def show_foo(self, id='foo1'):
        obj = getattr(fixtures, id)
        assert isinstance(obj, types.Foo)
        c.markup = markup_for_object('read', obj, 'a.foo1', { 'title': u'Foo #2' })
        return render('tests/page.html')

    def test_accordion_form(self):
        c.form_sections = []

        from collections import namedtuple
        P = namedtuple('P', ['heading', 'body'])
        
        def heading_markup(k):
            def markup():
                return 'Head #%s' %(k)
            return markup
        
        def body_markup(k):
            def markup():
                return 'Body #%s' %(k)
            return markup
        
        for y in ['a', 'b']:
            p = P(heading=heading_markup(y), body=body_markup(y))
            c.form_sections.append(p)

        #raise Exception('Break')
        c.form_class = 'form-horizontal' # 'form-horizontal'
        return render('tests/accordion-form.html')


