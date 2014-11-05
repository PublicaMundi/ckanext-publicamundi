import datetime
import logging
import copy
import json
import pprint
from collections import namedtuple

from pylons import url

from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

from ckanext.publicamundi.lib.dictization import unflatten
from ckanext.publicamundi.lib.util import Breakpoint
from ckanext.publicamundi.lib.util import to_json
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.types import Object
from ckanext.publicamundi.lib.metadata.widgets import (
    markup_for_field, markup_for_object, widget_for_object, widget_for_field)

from ckanext.publicamundi.lib.metadata.vocabularies import json_loader

from ckanext.publicamundi.tests import fixtures

import os.path
from ckanext.publicamundi.lib.metadata.xml_serializers import *
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import *
log1 = logging.getLogger(__name__)

import shutil
import requests
from unidecode import unidecode
content_types = {
            'json': 'application/json; charset=utf8',
            'xml': 'text/xml'
            }
PERMANENT_STORE = '/var/local/ckan/default/ofs/storage'
class TestsController(BaseController):

    def brk(self):
        raise Breakpoint()

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

    @classmethod
    def _get_action_context(cls):
        return {
            'model': model, 
            'session': model.Session, 
            'ignore_auth':True, 
            'api_version': 3,
        }
    
    def test_download(self, errors={}):
        return self.test_toxml(file_output='xml',name_or_id='title')


    def test_upload(self, errors={}):
        return render('package/upload_template.html', extra_vars={'errors':errors})

    def submit_upload(self):
        myfile = request.params.get('upload')
        link = request.params.get('url')

        # Case: File provided
        if isinstance(myfile, object):
            permanent_file = open(os.path.join(PERMANENT_STORE, myfile.filename.lstrip(os.sep)), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()
            return self.test_fromxml(filename = myfile.filename)
        # Case: Link provided
        elif link:
            try:
                r = requests.get(link)
                return self.test_fromxml(link=link)
            except Exception as ex:
                return self.test_upload(errors = {'Wrong url provided':['Please provide a correct url or upload an XML file']})
        else:
            return self.test_upload(errors = {'No file or link provided':['Please provide a url or upload an XML file']})

    def test_toxml(self, file_output='json', name_or_id=None):
        dataset = self._show(name_or_id)
        dataset_type = dataset.get('dataset_type')
        obj = dataset.get(dataset_type)

        if file_output == 'xml':
            response.headers['Content-Type'] = content_types['xml']
            ser = xml_serializer_for_object(obj)
            return [ser.dumps()]
        else:
            response.headers['Content-Type'] = content_types['json']
            data = obj.to_json()
            return [data]




    def test_fromxml(self, filename=None, link=None):
        if filename:
            try:
                infile = open(os.path.join(PERMANENT_STORE, filename), 'r')
            except:
                log1.info('Exception %s' % ex)
                os.remove(os.path.join(PERMANENT_STORE, filename))
                return self.test_upload(errors = {'Failure to read file':[ex]})
        elif link:
            infile = link

        ser = xml_serializer_for_object(InspireMetadata())
        try:
            e = etree.parse(infile)
        except Exception as ex:
            log1.info('Exception %s' % ex)
            if filename:
                os.remove(os.path.join(PERMANENT_STORE, filename))
            return self.test_upload(errors = {'Invalid XML file provided':[ex]})

        try:
            insp = ser.from_xml(e)
            errors = insp.validate(dictize_errors=True)
        except Exception as ex:
            log1.info('Exception %s' % ex)
            if filename:
                os.remove(os.path.join(PERMANENT_STORE, filename))
            return self.test_upload(errors = {'INSPIRE XML validation failure':[ex]})
        if self._package_exists(json_loader.munge(unidecode(insp.title))):
            return self.test_upload(errors = {'Package with the same name already exists':['Please change dataset title and try again']})

        if errors:
            # If there are validation errors redirect to stage 3 of editing for corrections 
            pkg = self._prepare_inspire_draft(insp)
            return toolkit.redirect_to(controller='package', action='new_metadata', id=pkg.get('name'))
        else:
            # Else package should be created correctly and user redirected to view page
            pkg = self._prepare_inspire(insp)
            return toolkit.redirect_to('dataset_read', id=pkg.get('name'))

    # Helpers

    def _prepare_inspire_draft(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data
        pkg_data['state'] = 'draft'

        pkg = self._create_or_update(pkg_data)
        return pkg


    def _prepare_inspire(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data

        pkg = self._create_or_update(pkg_data)
        return pkg

    def _create_or_update(self, data):
        context = self._get_action_context()
        # Purposefully skip validation at this stage
        context.update({ 'skip_validation': True })
        if self._package_exists(data.get('name')):
            # Not supporting package upload from xml
            pass
        else:
            pkg = toolkit.get_action ('package_create')(context, data_dict=data)
            log1.info('Created package %s' % pkg['name'])
        return pkg


    def _show(self, name_or_id):
        return toolkit.get_action ('package_show') (self._get_action_context(), data_dict = {'id': name_or_id})

    def _package_exists(self, name_or_id):
        return  name_or_id in toolkit.get_action ('package_list')(self._get_action_context(), data_dict={})

    def _check_result_for_read(self, data, result):
        pass
