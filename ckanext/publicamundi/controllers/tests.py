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

from ckanext.publicamundi.lib.util import Breakpoint
from ckanext.publicamundi.lib.util import to_json
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.types import Object
from ckanext.publicamundi.lib.metadata.widgets import \
    markup_for_field, markup_for_object

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
                    markup_for_field('edit', f, name_prefix='foo1', data=data) + \
                    toolkit.literal('<hr/>') + \
                    markup_for_field('read:bar', f, name_prefix='foo1', data=data)
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
                markup_for_object('edit:baz', obj, name_prefix='pt1', data=data) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read:boz', obj, name_prefix='pt1', data={'title': u'Point B'})
        })
        
        # 2.1 A TemporalExtent object
        obj = fixtures.dt1
        assert isinstance(obj, types.TemporalExtent)
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>TemporalExtent</code></h3>'),
            'body': markup_for_object('edit:faz.baz', obj, name_prefix='dt1', data={'title': u'Extent A'}) +
                toolkit.literal('<hr/>') + 
                markup_for_object('read', obj, name_prefix='dt1', data={ 'title': u'Extent B' })
        })
        
        # 2.2 A TemporalExtent object (with errors)
        obj = types.TemporalExtent(
            start=datetime.date(2014, 1, 1), end=datetime.date(2013, 1, 1))
        errs = obj.validate()
        errs = obj.dictize_errors(errs)
        assert isinstance(obj, types.TemporalExtent)
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>TemporalExtent</code></h3>'),
            'body': \
                markup_for_object('edit:faz.baz', obj, 
                    errors=errs, name_prefix='dt1', data={'title': u'Extent A'}) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read', obj, 
                    errors=errs, name_prefix='dt1', data={ 'title': u'Extent B' })
        })
       
        # 3. A PostalAddress object
        obj = types.PostalAddress(address=u'22 Acacia Avenue', postalcode=u'12345')
        c.form_sections.append({
            'heading': toolkit.literal('<h3>Object <code>PostalAddress</code></h3>'),
            'body': \
                markup_for_object('edit:comfortable', obj, 
                    name_prefix='contact_info', data={'title': u'Address A'}) + \
                toolkit.literal('<hr/>') + \
                markup_for_object('read', obj, 
                    name_prefix='contact_info', data={'title': u'Address B'})
        })
        
        # Render
        c.form_class = 'form-horizontal'
        return render('tests/accordion-form.html')

    def edit_foo(self, id='foo1'):
        '''Grab a Foo fixture and present an edit form 
        '''

        obj = getattr(fixtures, id)
        assert isinstance(obj, types.Foo)
        
        errors = obj.validate(dictize_errors=True)

        # Examine POSTed data
        if request.method == 'POST':
            # Parse request, filter-out empty values
            d = dict(filter(lambda t: t[1], request.params.items()))
            # Create a factory for this 
            factory = Object.Factory(schemata.IFoo, opts={
                'unserialize-keys': True,
                'unserialize-values': True,
            })
            obj = factory(d, is_flat=True)
            errors = obj.validate()
            if not errors:
                # Output a JSON dump of a valid object
                response.headers['Content-Type'] = 'application/json' 
                out = { 'status': 'success', 'obj': obj.to_dict() } 
                return to_json(out)
            else:
                # Prepare error dict for display
                errors = obj.dictize_errors(errors)
                #response.headers['Content-Type'] = 'application/json' 
                #out = { 'status': 'failure', 'errors': errors, 'obj': obj.to_dict() } 
                #return to_json(out)

        # Display form
        c.form_class = 'form-horizontal'
        c.form_errors = errors
        c.form_markup = markup_for_object('edit', obj, 
            errors = errors,
            name_prefix = '', 
            data = { 'title': u'Foo %s' % (id) }
        )
        return render('tests/form.html')

    def show_foo(self, id='foo1'):
        '''Grab a Foo fixture and show it with the requested format
        '''
        
        obj = getattr(fixtures, id)
        assert isinstance(obj, types.Foo)
        
        read_action = 'read'
        f = request.params.get('f')
        if f:
            read_action = 'read:%s' %(f)

        c.markup = markup_for_object(
            str(read_action), obj, name_prefix='a.foo1',
            data={ 'title': u'Foo %s' % (id) })
        
        return render('tests/page.html')
    
    def show_dataset(self, id):
        
        context = { 'model': model, 'session': model.Session }
        try:
            pkg_dict = toolkit.get_action('package_show')(context, { 'id': id })
        except toolkit.ObjectNotFound as ex:  
            abort(404)
        
        k = pkg_dict['dataset_type']
        obj = pkg_dict[k]
        
        #raise Breakpoint('Break')

        c.markup = markup_for_object('read:table', obj, errors={}, name_prefix=k, 
            data = {
                'title': u'%s: Metadata' %(pkg_dict['title'])
            })

        return render('tests/page.html')
        
    def test_template(self):
        '''A test tube for jinja2 templates ''' 
        return render('tests/test.html')

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


