import datetime
import logging
import copy
import json
import os
import random
from collections import namedtuple
from cgi import FieldStorage

from pylons import url

from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.helpers as h

from ckanext.publicamundi.lib.dictization import unflatten
from ckanext.publicamundi.lib.util import to_json, Breakpoint
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.types import Object
from ckanext.publicamundi.lib.metadata.widgets import (
    markup_for_field, markup_for_object, widget_for_object, widget_for_field)
from ckanext.publicamundi.tests import fixtures

log1 = logging.getLogger(__name__)

content_types = {
    'json': 'application/json; charset=utf8',
    'xml': 'text/xml'
}

class Controller(BaseController):

    def brk(self):
        raise Breakpoint()

    def test_translators(self):

        from ckanext.publicamundi.lib.metadata.i18n import translator_for
        md_1 = fixtures.inspire1
        tr = translator_for(md_1, 'el')
        md_2 = tr.get('en')

        assert False, 'Break'

    def test_csw_hooks(self, id):
        from ckanext.publicamundi.lib import pycsw_sync
        context = {'model': model, 'session': model.Session, 'api_version': 3}
        pkg_dict = toolkit.get_action('package_show')(context, {'id': id})
        pycsw_sync.create_or_update_record(context['session'], pkg_dict)
        return ['Done']
    
    def test_formatter(self):
        from ckanext.publicamundi.lib.metadata import formatter_for_field
        x = fixtures.inspire1
        f = x.get_field('spatial_resolution')
        fo = formatter_for_field(f, 'markup')
        s = fo.format()
        return [unicode(s)]
    
    def test_cache(self):
        from ckanext.publicamundi.cache_manager import get_cache

        cache1 = get_cache('test')

        def compute():
            log1.info(' ** i compute something **')
            return 42
        
        val = cache1.get('foo', createfunc=compute)
        assert False

    def test_dataapp(self):
        from paste.fileapp import DataApp
        app = DataApp('Ababoua')
        status, headers, app_it = request.call_application(app)
        assert False

    def mock_handle_upload(self):
        '''Mocks a upload handler.
        Returns a JSON dict that describes a successfully uploaded file.
        '''
        
        field_name = request.params.get('name')
        upload = request.params.get(field_name + '-upload') if field_name else 'upload'
        if not isinstance(upload, FieldStorage):
            abort(400, 'Expected a file upload')
        
        name = datetime.datetime.now().strftime('%s') + '-' + upload.filename
        l = toolkit.url_for(
            controller = 'ckanext.publicamundi.controllers.files:Controller',
            action = 'download_file',
            object_type = 'baz', 
            name_or_id = name,
            filename = upload.filename)
        
        n = random.randint(1000, 9999) 

        result = dict(name=name, url=l, size=n)
        response.headers['Content-Type'] = content_types['json']
        
        return [to_json(result)]
        
    def report_params(self):
        result = {}
        for k, f in request.params.items():
            if isinstance(f, FieldStorage) and hasattr(f, 'file'):
                fp, mimetype, filename, name = f.file, f.type, f.filename, f.name
                # Compute size
                fp.seek(0, 2) # move fp to the end
                size = fp.tell()
                fp.seek(0, 0) # reset fp
                # Report
                result[k] = {
                    'name': name,
                    'filename': filename,
                    'mimetype': mimetype,
                    'size': size,
                    'sample': fp.read(128).decode('utf-8') \
                        if mimetype.startswith('text/') else '<binary-data>'
                }
            else:
                result[k] = f
        
        response.headers['Content-Type'] = content_types['json']
        return [to_json(result)]
    
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
            'description': { 'description': u'Add a detailed description', },
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

    def get_field_markup_with_helper(self, id):
        x = getattr(fixtures, id)
       
        if request.method == 'POST':
            response.headers['Content-Type'] = 'application/json' 
            out = { tuple(k.split('.')): v for k, v in request.params.items() } 
            out = unflatten(out)
            return to_json(out)
        else:
            params = dict(request.params)
            
            k = params.pop('field', 'title')
            field = x.get_field(k)
            
            action = params.pop('action', 'edit')
            prefix = params.pop('prefix', id)
            
            extra_vars = copy.deepcopy(params) 
            extra_vars.update({
                'helper': True,
                'field': field,
                'action': str(action),
                'name_prefix': str(prefix),
            })
            
            return render('tests/field.html', extra_vars=extra_vars)
    
    def get_field_markup(self, id):
        x = getattr(fixtures, id)
       
        if request.method == 'POST':
            response.headers['Content-Type'] = 'application/json' 
            out = { tuple(k.split('.')): v for k, v in request.params.items() } 
            out = unflatten(out)
            return to_json(out)
        else:
            params = dict(request.params)
            k = params.pop('field', 'title')
            action = params.pop('action', 'edit')
            prefix = params.pop('prefix', id)
            
            field = x.get_field(k)
            field_markup = markup_for_field(str(action),
                field, name_prefix=str(prefix), errors=None, data=params)
            
            return render('tests/field.html', extra_vars={ 
                'field_markup': field_markup })

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
        assert isinstance(obj, types.FooMetadata)
        
        errors = obj.validate(dictize_errors=True)

        # Examine POSTed data
        if request.method == 'POST':
            # Parse request, filter-out empty values
            d = dict(filter(lambda t: t[1], request.params.items()))
            # Create a factory for this 
            factory = Object.Factory(schemata.IFooMetadata, opts={
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
        c.form_markup = markup_for_object('edit:datasetform', obj, 
            errors = errors,
            name_prefix = '', 
            data = { 'title': u'Foo %s' % (id) }
        )
        return render('tests/form.html')

    def show_foo(self, id='foo1'):
        '''Grab a Foo fixture and show it with the requested format
        '''
        
        obj = getattr(fixtures, id)
        assert isinstance(obj, types.FooMetadata)
        
        read_action = 'read'
        f = request.params.get('f')
        if f:
            read_action = 'read:%s' %(f)

        c.markup = markup_for_object(
            str(read_action), obj, name_prefix='a.foo1',
            data={ 'title': u'Foo %s' % (id) })

        return render('tests/page.html')
    
    def show_dataset(self, id):
        '''Show dataset's metadata formatted as a table'''
        
        context = { 'model': model, 'session': model.Session }
        try:
            pkg_dict = toolkit.get_action('package_show')(context, { 'id': id })
        except toolkit.ObjectNotFound as ex:  
            abort(404)
        
        k = pkg_dict['dataset_type']
        obj = pkg_dict[k]
        
        #raise Breakpoint('Break')

        data = { 'title': u'%s: Metadata' % (pkg_dict['title']) }
        c.markup = markup_for_object('read:table', obj, name_prefix=k, data=data)

        return render('tests/page.html')
        
    def test_template(self):
        '''A test tube for jinja2 templates ''' 
        return render('tests/test.html')

    def test_accordion_form(self):
        c.form_sections = []

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
    
    def test_upload_form(self):
        if request.method == 'POST':
            h.flash('Thanks for uploading data', 'alert-info')
            redirect(toolkit.url_for('/dataset'))
        return render('tests/upload-form.html')
   
