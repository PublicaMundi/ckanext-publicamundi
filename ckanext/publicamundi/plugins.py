# Plugins for ckanext-publicamundi

import time
import datetime
import json
import weberror
import logging
import geoalchemy

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi.model as publicamundi_model
import ckanext.publicamundi.lib.util as publicamundi_util
import ckanext.publicamundi.lib.metadata as publicamundi_metadata
import ckanext.publicamundi.lib.metadata.validators as publicamundi_validators
import ckanext.publicamundi.lib.actions as publicamundi_actions

from ckanext.publicamundi.lib.util import to_json, random_name
from ckanext.publicamundi.lib.metadata import \
    dataset_types, Object, ErrorDict, \
    serializer_for_object, serializer_for_key_tuple

_t = toolkit._

log1 = logging.getLogger(__name__)

class DatasetForm(p.SingletonPlugin, toolkit.DefaultDatasetForm):
    ''' A plugin that overrides the default dataset form '''
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)

    ## Define helper methods ## 

    @classmethod
    def publicamundi_helloworld(cls):
        ''' This is our simple helper function. '''
        markup = p.toolkit.render_snippet('snippets/hello.html', data={ 'name': 'PublicaMundi' })
        return p.toolkit.literal(markup)

    @classmethod
    def organization_list_objects(cls, org_names = []):
        ''' Make a action-api call to fetch the a list of full dict objects (for each organization) '''
        context = {
            'model': model,
            'session': model.Session,
            'user': toolkit.c.user,
        }

        options = { 'all_fields': True }
        if org_names and len(org_names):
            t = type(org_names[0])
            if   t is str:
                options['organizations'] = org_names
            elif t is dict:
                options['organizations'] = map(lambda org: org.get('name'), org_names)

        return logic.get_action('organization_list') (context, options)

    @classmethod
    def organization_dict_objects(cls, org_names = []):
        ''' Similar to organization_list_objects but returns a dict keyed to the organization name. '''
        results = {}
        for org in cls.organization_list_objects(org_names):
            results[org['name']] = org
        return results
    
    @classmethod
    def dataset_types(cls):
        '''Provide a dict of dataset types'''
        return dataset_types

    @classmethod
    def dataset_type_options(cls):
        '''Provide options for dataset-type (needed for select inputs)'''
        for name, spec in dataset_types.items():
            yield { 'value': name, 'text': spec['title'] }

    ## ITemplateHelpers interface ##

    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            'publicamundi_helloworld': self.publicamundi_helloworld,
            'random_name': random_name,
            'dataset_types': self.dataset_types,
            'dataset_type_options': self.dataset_type_options,
            'organization_list_objects': self.organization_list_objects,
            'organization_dict_objects': self.organization_dict_objects,
            'markup_for_field': publicamundi_metadata.markup_for_field,
            'markup_for_object': publicamundi_metadata.markup_for_object,
        }

    ## IConfigurer interface ##

    def update_config(self, config):
        ''' Setup the (fanstatic) resource library, public and template directory '''
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-publicamundi')

    ## IConfigurable interface ##

    def configure(self, config):
        ''' Apply configuration options to this plugin '''
        pass

    ## IRoutes interface ##

    def before_map(self, mapper):
        ''' Called before routes map is setup. '''

        mapper.connect ('/api/util/resource/mimetype_autocomplete',
            controller='ckanext.publicamundi.controllers.api:Controller', action='mimetype_autocomplete')

        #mapper.connect('tags', '/tags',
        #    controller='ckanext.publicamundi.controllers.tags:Controller', action='index')

        mapper.connect('publicamundi-tests', '/testing/publicamundi/{action}/{id}',
            controller='ckanext.publicamundi.controllers.tests:TestsController',)
        mapper.connect('publicamundi-tests', '/testing/publicamundi/{action}',
            controller='ckanext.publicamundi.controllers.tests:TestsController',)

        return mapper

    ## IActions interface ##

    def get_actions(self):
        return {
            'mimetype_autocomplete': publicamundi_actions.mimetype_autocomplete,
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

    def _modify_package_schema(self, schema):
        log1.debug(' ** _modify_package_schema(): Building schema ...')
         
        from ckanext.publicamundi.lib.metadata.validators import \
            is_dataset_type, get_field_edit_processor, \
            preprocess_dataset_for_edit, postprocess_dataset_for_edit

        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        default_initializer = toolkit.get_validator('default')

        # Add dataset-type, the field that distinguishes metadata formats
        
        schema['dataset_type'] = [
            default_initializer('ckan'),
            convert_to_extras,
            is_dataset_type,
        ]
       
        # Add field-level validators/converters
        
        # Note We provide a union of fields for all supported schemata.
        # Of course, not all of them will be present in a specific dataset,
        # so any "required" constraint cannot be applied here.

        for dt, dt_spec in dataset_types.items():
            flattened_fields = dt_spec.get('class').get_flattened_fields(opts={
                'serialize-keys': True,
                'key-prefix': dt_spec.get('key_prefix', dt)
            })
            for field_name, field in flattened_fields.items():
                # Build chain of processors for field
                schema[field_name] = [ 
                    ignore_missing,
                    get_field_edit_processor(field),
                ]
        
        # Add before/after package-level processors

        schema['__before'].insert(-1, preprocess_dataset_for_edit)

        if not schema.has_key('__after'):
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset_for_edit)
        
        return schema

    def create_package_schema(self):
        log1.debug(' ** create_package_schema(): Building schema ...')
        schema = super(DatasetForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        log1.debug(' ** update_package_schema(): Building schema ...')
        schema = super(DatasetForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(DatasetForm, self).show_package_schema()
        
        log1.debug(' ** show_package_schema(): Building schema ...')
        
        from ckanext.publicamundi.lib.metadata.validators import \
            get_field_read_processor, \
            preprocess_dataset_for_read, postprocess_dataset_for_read

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        
        check_not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')
        
        schema['dataset_type'] = [ convert_from_extras, check_not_empty ]
       
        # Add field-level converters

        for dt, dt_spec in dataset_types.items():
            flattened_fields = dt_spec.get('class').get_flattened_fields(opts={
                'serialize-keys': True,
                'key-prefix': dt_spec.get('key_prefix', dt)
            })
            for field_name, field in flattened_fields.items():
                schema[field_name] = [ 
                    convert_from_extras, 
                    ignore_missing, 
                    get_field_read_processor(field),
                ]
          
        # Add before/after package-level processors
        
        schema['__before'].insert(-1, preprocess_dataset_for_read)
        
        if not schema.has_key('__after'):
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset_for_read)
        
        return schema

    def setup_template_variables(self, context, data_dict):
        ''' Setup (add/modify/hide) variables to feed the template engine.
        This is done through through toolkit.c (template thread-local context object).
        '''
        
        super(DatasetForm, self).setup_template_variables(context, data_dict)
        
        #assert False

        c = toolkit.c
        c.publicamundi_magic_number = 99

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

class PackageController(p.SingletonPlugin):
    ''' Hook into the package controller '''
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    ## IConfigurable interface ##

    def configure(self, config):
        ''' Apply configuration options to this plugin '''
        pass

    ## IPackageController interface ##

    def after_create(self, context, pkg_dict):
        '''
        Extensions will receive the validated data dict after the package has been created
        Note that the create method will return a package domain object, which may not include all fields.
        Also the newly created package id will be added to the dict.
        At this point, the package is possibly in 'draft' state so most Action-API (targeting on the
        package itself) calls will fail.
        '''
        log1.debug('A package was created: %s', to_json(pkg_dict, indent=4))
        self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_update(self, context, pkg_dict):
        '''
        Extensions will receive the validated data dict after the package has been updated
        (Note that the edit method will return a package domain object, which may not include all fields).
        '''
        log1.debug('A package was updated: %s', to_json(pkg_dict, indent=4))
        self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_delete(self, context, pkg_dict):
        '''
        Extensions will receive the data dict (typically containing just the package id) after the package has been deleted.
        '''
        log1.debug('A package was deleted: %s', json.dumps(pkg_dict, indent=3))
        self._delete_csw_record(context['session'], pkg_dict)
        pass

    def after_show(self, context, pkg_dict):
        '''
        Extensions will receive the validated data dict after the package is ready for display
        (Note that the read method will return a package domain object, which may not include all fields).
        '''
        #log1.info('A package is shown: %s', pkg_dict)
        pass

    def before_search(self, search_params):
        '''
        Extensions will receive a dictionary with the query parameters just before are sent to SOLR backend,
        and should return a modified (or not) version of it.
        Parameter search_params will include an "extras" dictionary with all values from fields
        starting with "ext_", so extensions can receive user input from specific fields. This "extras"
        dictionary will not affect SOLR results, but can be later be used by the after_search callback.
        '''
        #search_params['q'] = 'extras_boo:*';
        #search_params['extras'] = { 'ext_boo': 'far' }
        return search_params

    def after_search(self, search_results, search_params):
        '''
        Extensions will receive the search results, as well as the search parameters, and should return a modified
        (or not) object with the same structure:
            {"count": "", "results": "", "facets": ""}
        Note that count and facets may need to be adjusted if the extension changed the results for some reason.
        Parameter search_params will include an extras dictionary with all values from fields starting with "ext_", so
        extensions can receive user input from specific fields. For example, the ckanext-spatial extension recognizes
        the "ext_bbox" parameter (inside "extras" dict) and handles it appropriately by filtering the results on one
        more condition (filters out those not contained in the specified bounding box)
        '''
        #raise Exception('Breakpoint')
        return search_results

    def before_index(self, pkg_dict):
        '''
        Extensions will receive what will be given to SOLR for indexing. This is essentially a flattened dict
        (except for multli-valued fields such as tags) of all the terms sent to the indexer. The extension can modify
        this by returning an altered version.
        '''
        return pkg_dict

    def before_view(self, pkg_dict):
        '''
        Extensions will recieve this before the dataset gets displayed. The dictionary returned will be the one
        that gets sent to the template.
        '''
        # An IPackageController can add/hide/transform package fields before sent to the template.
        extras = pkg_dict.get('extras', [])
        # or we can translate keys ...
        field_key_map = {
            u'updated_at': _t(u'Updated'),
            u'created_at': _t(u'Created'),
        }
        for item in extras:
            k = item.get('key')
            item['key'] = field_key_map.get(k, k)
        return pkg_dict

    def _create_or_update_csw_record(self, session, pkg_dict):
        ''' Sync dataset fields to CswRecord fields '''
        #raise Exception('Break')
        from geoalchemy import WKTSpatialElement
        from ckanext.publicamundi.lib.util import geojson_to_wkt
        # Populate record fields
        record = session.query(publicamundi_model.CswRecord).get(pkg_dict['id'])
        if not record:
            log1.info('Creating CswRecord %s', pkg_dict.get('id'))
            record = publicamundi_model.CswRecord(pkg_dict.get('id'), name=pkg_dict.get('name'))
            session.add(record)
        else:
            log1.info('Updating CswRecord %s', pkg_dict.get('id'))
        extras = { item['key']: item['value'] for item in pkg_dict.get('extras', []) }
        record.title = pkg_dict.get('title')
        if 'spatial' in extras:
            record.geom = WKTSpatialElement(geojson_to_wkt(extras.get('spatial')))
        # Persist object
        session.commit()
        log1.info('Saved CswRecord %s (%s)', record.id, record.name)
        return

    def _delete_csw_record(self, session, pkg_dict):
        record = session.query(publicamundi_model.CswRecord).get(pkg_dict['id'])
        if record:
            session.delete(record)
            session.commit()
            log1.info('Deleted CswRecord %s', pkg_dict['id'])
        return

class ErrorHandler(p.SingletonPlugin):
    ''' Fixes CKAN's buggy errorware configuration '''
    p.implements(p.IConfigurer, inherit=True)

    @staticmethod
    def _exception_as_mime_message(exc_data, to_addresses, from_address, prefix):
        from weberror.reporter  import as_str
        from weberror.formatter import format_text

        msg = weberror.reporter.MIMEText(format_text(exc_data)[0])
        msg['Subject'] = as_str(prefix + exc_data.exception_value)
        msg['From'] = as_str(from_address)
        msg['To'] = as_str(", ".join(to_addresses))
        msg.set_type('text/plain')
        msg.set_param('charset', 'UTF-8')
        return msg

    def update_config(self, config):
        from weberror.reporter import EmailReporter as error_reporter
        # override default config options for pylons errorware
        error_config = config['pylons.errorware']
        error_config.update({
            'error_subject_prefix' : config.get('ckan.site_title') + ': ',
            'from_address' : config.get('error_from_address'),
            'smtp_server'  : config.get('smtp.server'),
            'smtp_username': config.get('smtp.username'),
            'smtp_password': config.get('smtp.password'),
            'smtp_use_tls' : config.get('smtp.use_tls'),
        })
        # monkey-patch email error reporter 
        error_reporter.assemble_email = lambda t,exc_data: self._exception_as_mime_message (\
            exc_data, to_addresses=t.to_addresses, from_address=t.from_address, prefix=t.subject_prefix)

