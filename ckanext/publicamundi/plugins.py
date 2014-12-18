import re
import datetime
import json
import weberror
import logging
import string
import urllib
import geoalchemy
from itertools import chain, ifilter
from routes.mapper import SubMapper

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi.model as ext_model
import ckanext.publicamundi.lib.metadata as ext_metadata
import ckanext.publicamundi.lib.metadata.validators as ext_validators
import ckanext.publicamundi.lib.actions as ext_actions
import ckanext.publicamundi.lib.template_helpers as ext_template_helpers
import ckanext.publicamundi.lib.pycsw_sync as ext_pycsw_sync

from ckanext.publicamundi.lib.util import (to_json, random_name, Breakpoint)
from ckanext.publicamundi.lib.metadata import dataset_types

_ = toolkit._
asbool = toolkit.asbool
aslist = toolkit.aslist
url_for = toolkit.url_for

log1 = logging.getLogger(__name__)

class DatasetForm(p.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''Override the default dataset form.
    '''
    
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IFacets, inherit=True)

    _debug = False

    _dataset_types = None

    ## Define helper methods ## 

    @classmethod
    def dataset_types(cls):
        '''Provide a dict of supported dataset types'''
        return cls._dataset_types

    @classmethod
    def dataset_type_options(cls):
        '''Provide options for dataset-type (needed for selects)'''
        for k, spec in cls._dataset_types.items():
            yield { 'value': k, 'text': spec['title'] }

    ## ITemplateHelpers interface ##

    def get_helpers(self):
        '''Return a dict of named helper functions (ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''

        return {
            'debug': lambda: self._debug,
            'random_name': random_name,
            'filtered_list': ext_template_helpers.filtered_list,
            'dataset_types': self.dataset_types,
            'dataset_type_options': self.dataset_type_options,
            'organization_objects': ext_template_helpers.get_organization_objects,
            'make_metadata_object': ext_metadata.make_metadata_object,
            'markup_for_field': ext_metadata.markup_for_field,
            'markup_for_object': ext_metadata.markup_for_object,
            'markup_for': ext_metadata.markup_for,
            'resource_ingestion_result': ext_template_helpers.resource_ingestion_result,
        }

    ## IConfigurer interface ##

    def update_config(self, config):
        '''Configure CKAN (Pylons) environment'''

        # Setup static resources

        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_template_directory(config, 'templates_legacy')
        p.toolkit.add_resource('public', 'ckanext-publicamundi')
        
        return

    ## IConfigurable interface ##

    def configure(self, config):
        '''Pass configuration to plugins and extensions'''
        
        cls = type(self)

        # Are we in debug mode?

        cls._debug = asbool(config['global_conf']['debug'])
        
        # Set supported dataset types

        type_keys = aslist(config['ckanext.publicamundi.dataset_types'])
        cls._dataset_types = { k: spec
            for k, spec in dataset_types.items() if k in type_keys }

        # Modify the pattern for valid names for {package, groups, organizations}
        
        if asbool(config.get('ckanext.publicamundi.validation.relax_name_pattern')):
            logic.validators.name_match = re.compile('[a-z][a-z0-9~_\-]*$')
            log1.info('Using pattern for valid names: %r', 
                logic.validators.name_match.pattern)
              
        # Setup extension-wide cache manager

        from ckanext.publicamundi import cache_manager
        cache_manager.setup(config)
    
        return

    ## IRoutes interface ##

    def before_map(self, mapper):
        '''Setup routes before CKAN defines core routes.'''

        api_controller = 'ckanext.publicamundi.controllers.api:Controller'
  
        with SubMapper(mapper, controller=api_controller) as m:
        
            m.connect(
                '/api/publicamundi/util/resource/mimetype_autocomplete',
                action='resource_mimetype_autocomplete')
        
            m.connect(
                '/api/publicamundi/util/resource/format_autocomplete',
                action='resource_format_autocomplete')

            m.connect(
                '/api/publicamundi/vocabularies',
                action='vocabularies_list')
         
            m.connect(
                '/api/publicamundi/vocabularies/{name}',
                action='vocabulary_get')
        
            m.connect(
                '/api/publicamundi/dataset/export/{name_or_id}', 
                action='dataset_export')
        
            m.connect(
                '/api/publicamundi/dataset/import', 
                action='dataset_import',
                conditions=dict(method=['POST']))

        user_controller = 'ckanext.publicamundi.controllers.user:UserController'

        with SubMapper(mapper, controller=user_controller) as m:
            
            # Fixme: unneeded parameters to mapper.connect ?

            m.connect(
                'user_dashboard_resources',
                '/dashboard/resources',
                 action='show_dashboard_resources')
            
            m.connect(
                'admin_page_resources', 
                '/user/resources',
                 action='show_admin_page_resources')
            
            m.connect(
                'reject_resource',
                '/{parent}/resources/reject/{resource_id}',
                action='reject_resource')
            
            m.connect(
                'identify_vector_resource', # Fixme: adapt
                '/{parent}/resources/identify_vector/{resource_id}',
                 action='identify_resource',
                 storer_type='vector')
            
            m.connect(
                'render_ingestion',
                '/{parent}/resources/ingest/{resource_id}',
                action='render_ingestion_template')
      
        files_controller = 'ckanext.publicamundi.controllers.files:Controller'
        
        with SubMapper(mapper, controller=files_controller) as m:
        
            m.connect(
                '/publicamundi/files/{object_type}/{name_or_id}/download/{filename:.*?}',
                action='download_file')
        
            m.connect(
                '/publicamundi/files/{object_type}', 
                action='upload_file',
                conditions=dict(method=['POST']))
        
        package_controller = 'ckanext.publicamundi.controllers.package:Controller'

        mapper.connect(
            '/dataset/import_metadata',
            controller=package_controller,
            action='import_metadata')
       
        tests_controller = 'ckanext.publicamundi.controllers.tests:Controller'

        mapper.connect(
            'publicamundi-tests', 
            '/testing/publicamundi/{action}/{id}',
            controller=tests_controller)
        
        mapper.connect(
            'publicamundi-tests', 
            '/testing/publicamundi/{action}',
            controller=tests_controller)

        return mapper

    ## IActions interface ##

    def get_actions(self):
        return {
            'mimetype_autocomplete': ext_actions.autocomplete.mimetype_autocomplete,
            'dataset_export': ext_actions.package.dataset_export,
            'dataset_import': ext_actions.package.dataset_import,
        }

    ## IDatasetForm interface ##

    def is_fallback(self):
        '''
        Return True to register this plugin as the default handler for
        package types not handled by any other IDatasetForm plugin.
        '''
        return True

    def package_types(self):
        '''
        This plugin doesn't handle any special package types, it just
        registers itself as the default (above).
        '''
        return []

    def __modify_package_schema(self, schema):
        '''Define modify schema for both create/update operations.
        '''

        check_not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        default_initializer = toolkit.get_validator('default')
        
        # Add dataset-type, the field that distinguishes metadata formats

        is_dataset_type = ext_validators.is_dataset_type
        schema['dataset_type'] = [
            default_initializer('ckan'), convert_to_extras, is_dataset_type,
        ]
       
        # Add package field-level validators/converters
        
        # Note We provide a union of fields for all supported schemata.
        # Of course, not all of them will be present in a specific dataset,
        # so any "required" constraint cannot be applied here.

        get_field_processor = ext_validators.get_field_edit_processor
        
        for dt, dt_spec in self._dataset_types.items():
            flattened_fields = dt_spec.get('class').get_flattened_fields(opts={
                'serialize-keys': True,
                'key-prefix': dt_spec.get('key_prefix', dt)
            })
            for field_name, field in flattened_fields.items():
                # Build chain of processors for field
                schema[field_name] = [ 
                    ignore_missing, get_field_processor(field),
                ]
        
        # Add before/after package-level processors

        preprocess_dataset = ext_validators.preprocess_dataset_for_edit
        postprocess_dataset = ext_validators.postprocess_dataset_for_edit
        
        schema['__before'].insert(-1, preprocess_dataset)

        if not '__after' in schema:
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset)
        
        # Add or replace resource field-level validators/converters

        guess_resource_type = ext_validators.guess_resource_type_if_empty

        schema['resources'].update({
            'resource_type': [
                guess_resource_type, string.lower, unicode],
            'format': [
                check_not_empty, string.lower, unicode],
        })

        # Done, return updated schema

        return schema

    def create_package_schema(self):
        schema = super(DatasetForm, self).create_package_schema()
        schema = self.__modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(DatasetForm, self).update_package_schema()
        schema = self.__modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(DatasetForm, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        
        check_not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')
        
        schema['dataset_type'] = [convert_from_extras, check_not_empty]
       
        # Add package field-level converters
        
        get_field_processor = ext_validators.get_field_read_processor

        for dt, dt_spec in self._dataset_types.items():
            flattened_fields = dt_spec.get('class').get_flattened_fields(opts={
                'serialize-keys': True,
                'key-prefix': dt_spec.get('key_prefix', dt)
            })
            for field_name, field in flattened_fields.items():
                schema[field_name] = [ 
                    convert_from_extras, ignore_missing, get_field_processor(field)
                ]
          
        # Add before/after package-level processors
        
        preprocess_dataset = ext_validators.preprocess_dataset_for_read
        postprocess_dataset = ext_validators.postprocess_dataset_for_read

        schema['__before'].insert(-1, preprocess_dataset)
        
        if not '__after' in schema:
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset)
        
        return schema

    def setup_template_variables(self, context, data_dict):
        ''' Setup (add/modify/hide) variables to feed the template engine.
        This is done through through toolkit.c (template thread-local context object).
        '''
        
        super(DatasetForm, self).setup_template_variables(context, data_dict)

        c = toolkit.c
        c.publicamundi_magic_number = 99
        
        if c.search_facets:
            # Provide label functions for certain facets
            if not c.facet_labels:
                c.facet_labels = {
                    'res_format': lambda t: t['display_name'].upper()
                }

    # Note for all *_template hooks: 
    # We choose not to modify the path for each template (so we simply call super()). 
    # If a specific template's behaviour needs to be overriden, this can be done by 
    # means of template inheritance (e.g. Jinja2 `extends' or CKAN `ckan_extends')

    def new_template(self):
        return super(DatasetForm, self).new_template()

    def read_template(self):
        return super(DatasetForm, self).read_template()

    def edit_template(self):
        return super(DatasetForm, self).edit_template()

    def comments_template(self):
        return super(DatasetForm, self).comments_template()

    def search_template(self):
        return super(DatasetForm, self).search_template()

    def history_template(self):
        return super(DatasetForm, self).history_template()

    ## IPackageController interface ##
    
    def after_create(self, context, pkg_dict):
        log1.debug('after_create: Package %s is created', pkg_dict.get('name'))
        pass

    def after_update(self, context, pkg_dict):
        log1.debug('after_update: Package %s is updated', pkg_dict.get('name'))
        pass

    def after_show(self, context, pkg_dict):
        '''Hook into the validated data dict after the package is ready for display. 
        
        The main tasks here are:
         * Fix types for serialized dataset_type-related values (converted to unicode,
           whereas should be str).
         * Convert dataset_type-related parts of pkg_dict to a nested dict or an object.

        This hook is for reading purposes only, i.e for template variables, api results, 
        form initial values etc. It should *not* affect the way the read schema is used: 
        schema items declared at read_package_schema() should not be removed (though their 
        values can be changed!).
        '''

        is_validated = context.get('validate', True)
        for_view = context.get('for_view', False)
        
        log1.debug('after_show: Package %s is shown: view=%s validated=%s api=%s', 
            pkg_dict.get('name'), for_view, is_validated, context.get('api_version'))
        
        if not is_validated:
            # Noop: the extras are not yet promoted to 1st-level fields
            return

        # Determine dataset_type-related parameters for this package
        
        dt = pkg_dict.get('dataset_type')
        if not dt:
            # Noop: cannot recognize dataset-type (pkg_dict has raw extras?)
            return

        dt_spec = self._dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # Fix types, create flat object dict
        
        # Note If we attempt to pop() flat keys here (e.g. to replace them by a 
        # nested structure), resource forms will clear all extra fields !!

        prefix = key_prefix + '.'
        keys = filter(lambda k: k.startswith(prefix), pkg_dict.iterkeys())
        obj_dict = {}
        for k in keys:
            k1 = k[len(prefix):]
            obj_dict[k1] = pkg_dict[k] = str(pkg_dict[k])

        # Objectify 
        
        obj_factory = dt_spec.get('class')
        obj = obj_factory().from_dict(obj_dict, is_flat=True, opts={
            'unserialize-keys': True,
            'unserialize-values': 'default',
        })

        pkg_dict[key_prefix] = obj
        
        # Note We use this bit of hack when package is shown directly from the
        # action api, normally at /api/action/(package|dataset)_show.
            
        r = toolkit.c.environ['pylons.routes_dict']
        if (r['controller'] == 'api' and r.get('action') == 'action' and 
                r.get('logic_function') in (
                    'package_show', 'package_create', 'package_update',
                    'dataset_show', 'dataset_create', 'dataset_update')):
            # Remove flat field values (won't be needed anymore)
            for k in keys:
                pkg_dict.pop(k)
            # Dictize obj so that json.dumps can handle it
            pkg_dict[key_prefix] = obj.to_dict(flat=False, opts={
                'serialize-values': 'json-s' 
            })
         
        return pkg_dict
     
    def before_search(self, search_params):
        '''Return a modified (or not) version of the query parameters.
        '''
        #search_params['q'] = 'extras_boo:*';
        #search_params['extras'] = { 'ext_boo': 'far' }
        return search_params
   
    def after_search(self, search_results, search_params):
        '''Receive the search results, as well as the search parameters, and
        return a modified (or not) result with the same structure.
        '''
        #raise Exception('Breakpoint')
        return search_results

    def before_index(self, pkg_dict):
        '''Receive what will be given to SOLR for indexing.
        
        This is essentially a flattened dict (except for multi-valued fields 
        such as tags) of all the terms sent to the indexer.
        '''
        log1.debug('before_index: Package %s is indexed', pkg_dict.get('name'))
        return pkg_dict

    def before_view(self, pkg_dict):
        '''Receive the validated package dict before it is sent to the template. 
        '''

        log1.debug('before_view: Package %s is prepared for view', pkg_dict.get('name'))
        
        dt = pkg_dict.get('dataset_type')
        dtspec = self._dataset_types.get(dt) if dt else None
        pkg_name, pkg_id = pkg_dict['name'], pkg_dict['id']
        
        # Provide alternative download links for dataset's metadata 
        
        if dt:
            download_links = pkg_dict.get('download_links', []) 
            if not download_links:
                pkg_dict['download_links'] = download_links
            download_links.extend([
                {
                    'title': dtspec['title'],
                    'url': url_for('/api/action/dataset_show', id=pkg_name),
                    'weight': 0,
                    'format': 'json',
                },
                {
                    'title': dtspec['title'],
                    'url': url_for(
                        controller='ckanext.publicamundi.controllers.api:Controller',
                        action='dataset_export',
                        name_or_id=pkg_name),
                    'weight': 5,
                    'format': 'xml',
                },
            ])
        
        return pkg_dict

    ## IResourceController interface ##

    def before_show(self, resource_dict):
        '''Receive the validated data dict before the resource is ready for display.
        '''
        
        # Normalize resource format (#66)
        # Note ckan.lib.dictization.model_dictize:resource_dictize converts only
        # some of the formats to uppercase (?), which leads to mixed cases.
        resource_dict['format'] = resource_dict['format'].lower()
        
        return resource_dict

    ## IFacets interface ##

    def dataset_facets(self, facets_dict, package_type):
        '''Update the facets_dict and return it.
        '''
        if package_type == 'dataset':
            # Todo Maybe reorder facets
            pass
        return facets_dict

class PackageController(p.SingletonPlugin):
    '''Hook into the package controller
    '''

    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    
    csw_output_schemata = {
        'dc': 'http://www.opengis.net/cat/csw/2.0.2',
        'iso-19115': 'http://www.isotc211.org/2005/gmd',
        'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
        'atom': 'http://www.w3.org/2005/Atom',
        'nasa-dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    }
   
    _pycsw_config_file = None
    _pycsw_service_endpoint = None

    ## IConfigurable interface ##

    def configure(self, config):
        '''Apply configuration settings to this plugin
        '''
        
        cls = type(self)

        site_url = config['ckan.site_url']
        cls._pycsw_config_file = config.get(
            'ckanext.publicamundi.pycsw.config', 
            'pycsw.ini')
        cls._pycsw_service_endpoint = config.get(
            'ckanext.publicamundi.pycsw.service_endpoint', 
            '%s/csw' % (site_url.rstrip('/')))
        
        ext_pycsw_sync.setup(site_url, self._pycsw_config_file)

        return

    ## IPackageController interface ##

    def after_create(self, context, pkg_dict):
        '''Extensions will receive the validated data dict after the package has been created
       
        Note that the create method will return a package domain object, which may not 
        include all fields. Also the newly created package id will be added to the dict.
        At this point, the package is possibly in 'draft' state so most Action-API 
        (targeting on the package itself) calls will fail.
        '''
        
        log1.debug('A package was created: %s', pkg_dict['id'])
        self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_update(self, context, pkg_dict):
        '''Extensions will receive the validated data dict after the package has been updated
        
        Note that the edit method will return a package domain object, which may not include 
        all fields.
        '''
        
        log1.debug('A package was updated: %s', pkg_dict['id'])
        self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_delete(self, context, pkg_dict):
        '''Extensions will receive the data dict (typically containing just the package id)
        after the package has been deleted.
        '''

        log1.debug('A package was deleted: %s', pkg_dict['id'])
        self._delete_csw_record(context['session'], pkg_dict)
        pass

    def after_show(self, context, pkg_dict):
        '''Receive the validated data dict after the package is ready for display. 
        
        Note that the read method will return a package domain object (which may 
        not include all fields).
        '''
        
        #log1.info('A package is shown: %s', pkg_dict)
        pass

    def before_search(self, search_params):
        '''Extensions will receive a dictionary with the query parameters just before are
        sent to SOLR backend, and should return a modified (or not) version of it.
        
        Parameter search_params will include an "extras" dictionary with all values from 
        fields starting with "ext_", so extensions can receive user input from specific fields.
        This "extras" dictionary will not affect SOLR results, but can be later be used by the
        after_search callback.
        '''

        #search_params['q'] = 'extras_boo:*';
        #search_params['extras'] = { 'ext_boo': 'far' }
        return search_params

    def after_search(self, search_results, search_params):
        '''Extensions will receive the search results, as well as the search parameters,
        and should return a modified (or not) object with the same structure:
            {"count": "", "results": "", "facets": ""}
        
        Note that count and facets may need to be adjusted if the extension changed the results
        for some reason. Parameter search_params will include an extras dictionary with all 
        values from fields starting with "ext_", so extensions can receive user input from 
        specific fields. For example, the ckanext-spatial extension recognizes the "ext_bbox"
        parameter (inside "extras" dict) and handles it appropriately by filtering the results on one
        more condition (filters out those not contained in the specified bounding box)
        '''
        
        #raise Exception('Breakpoint')
        return search_results

    def before_index(self, pkg_dict):
        '''Extensions will receive what will be given to SOLR for indexing. This is essentially
        a flattened dict (except for multli-valued fields such as tags) of all the terms sent
        to the indexer. The extension can modify this by returning an altered version.
        '''
        return pkg_dict

    def before_view(self, pkg_dict):
        '''Extensions will recieve this before the dataset gets displayed.
        
        The dictionary returned will be the one sent to the template.
        '''
        
        dt = pkg_dict.get('dataset_type')
        pkg_name, pkg_id = pkg_dict['name'], pkg_dict['id']

        # Provide CSW-backed download links for dataset's metadata 
       
        if dt:
            download_links = pkg_dict.get('download_links', []) 
            if not download_links:
                pkg_dict['download_links'] = download_links
            download_links.extend([
                {
                    'title': 'DC',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='dc', output_format='application/xml'),
                    'weight': 10,
                    'format': 'xml',
                },
                {
                    'title': 'DC',
                    'generator': 'CSW',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='dc', output_format='application/json'),
                    'weight': 15,
                    'format': 'json',
                },
                {
                    'title': 'ISO-19115',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='iso-19115', output_format='application/xml'),
                    'weight': 15,
                    'format': 'xml',
                },
                {
                    'title': 'ISO-19115',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='iso-19115', output_format='application/json'),
                    'weight': 20,
                    'format': 'json',
                },
                {
                    'title': 'FGDC',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='fgdc', output_format='application/xml'),
                    'weight': 25,
                    'format': 'xml',
                },
                {
                    'title': 'Atom',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='atom', output_format='application/xml'),
                    'weight': 30,
                    'format': 'xml',
                },
                {
                    'title': 'NASA-DIF',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='nasa-dif', output_format='application/xml'),
                    'weight': 35,
                    'format': 'xml',
                },
            ])
        
        return pkg_dict

    ## Helpers ##
    
    def _build_csw_request_url(self, pkg_id, output_schema='dc', output_format=None):
        '''Build a GetRecordById request to a CSW endpoint
        '''
        
        qs_params = {
            'service': 'CSW',
            'version': '2.0.2',
            'request': 'GetRecordById',
            'ElementSetName': 'full',
            'OutputSchema': self.csw_output_schemata.get(output_schema, ''),
            'Id': pkg_id,
        }
        
        if output_format:
            qs_params['OutputFormat'] = output_format
 
        return self._pycsw_service_endpoint + '?' + urllib.urlencode(qs_params)

    def _create_or_update_csw_record(self, session, pkg_dict):
        '''Sync dataset with CSW record'''
        
        pkg_id = pkg_dict['id']

        if pkg_dict.get('state', 'active') != 'active':
            log1.info(
                'Skipped sync of non-active dataset %s to CSW record' % (pkg_id))
            return

        record = ext_pycsw_sync.create_or_update_record(session, pkg_dict)
        if record: 
            log1.info('Saved CswRecord %s (%s)', record.identifier, record.title)
        else:
            log1.warning('Failed to save CswRecord for dataset %s' %(pkg_id))
        
        return

    def _delete_csw_record(self, session, pkg_dict):
        '''Delete CSW record'''
        record = ext_pycsw_sync.delete_record(session, pkg_dict)
        if record:
            log1.info('Deleted CswRecord for dataset %s', pkg_dict['id'])  
        return

class ErrorHandler(p.SingletonPlugin):
    '''Fix CKAN's buggy errorware configuration'''
    p.implements(p.IConfigurer, inherit=True)

    @staticmethod
    def _exception_as_mime_message(exc_data, to_addresses, from_address, prefix):
        from weberror.reporter  import as_str
        from weberror.formatter import format_text

        msg = weberror.reporter.MIMEText(format_text(exc_data)[0])
        msg['Subject'] = as_str(prefix + exc_data.exception_value)
        msg['From'] = as_str(from_address)
        msg['Reply-To'] = as_str(from_address)
        msg['To'] = as_str(", ".join(to_addresses))
        msg.set_type('text/plain')
        msg.set_param('charset', 'UTF-8')
        return msg

    def update_config(self, config):
        from weberror.reporter import EmailReporter as error_reporter
        
        # Override default config options for pylons errorware
        error_config = config['pylons.errorware']
        error_config.update({
            'error_subject_prefix' : config.get('ckan.site_title') + ': ',
            'from_address' : config.get('error_email_from'),
            'smtp_server'  : config.get('smtp.server'),
            'smtp_username': config.get('smtp.user'),
            'smtp_password': config.get('smtp.password'),
            'smtp_use_tls' : config.get('smtp.starttls'),
        })
        
        # Monkey-patch email error reporter 
        error_reporter.assemble_email = lambda t, exc: self._exception_as_mime_message(
            exc, 
            to_addresses=t.to_addresses, 
            from_address=t.from_address,
            prefix=t.subject_prefix)

class SpatialDatasetForm(DatasetForm):
    '''Extend the dataset-form to recognize and read/write the `spatial` extra field.
    This extension only serves as a bridge to ckanext-spatial `spatial_metadata` 
    plugin.
    
    Note: 
    This should be part of a the ordinary `publicamundi_dataset` plugin (when it
    gets decoupled from schema-handling logic!).
    '''
    
    ## IDatasetForm interface ##

    def create_package_schema(self):
        schema = super(SpatialDatasetForm, self).create_package_schema()
        return self.__modify_package_schema(schema)

    def update_package_schema(self):
        schema = super(SpatialDatasetForm, self).update_package_schema()
        return self.__modify_package_schema(schema)
    
    def show_package_schema(self):
        schema = super(SpatialDatasetForm, self).show_package_schema()
        
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')
       
        schema['spatial'] = [convert_from_extras, ignore_missing]

        return schema
    
    def __modify_package_schema(self, schema):
        
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        
        schema['spatial'] = [ignore_empty, convert_to_extras]
        
        return schema

