# Plugins for ckanext-publicamundi

import json, jsonpickle, time

import logging

import ckan.model           as model
import ckan.plugins         as p
import ckan.plugins.toolkit as toolkit
import ckan.logic           as logic

import weberror

_t = toolkit._

log1 = logging.getLogger(__name__)

class DatasetForm(p.SingletonPlugin, toolkit.DefaultDatasetForm):
    ''' A plugin that overrides the default dataset form '''
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)

    ## Define helper methods ## 

    @classmethod
    def publicamundi_helloworld(cls):
        ''' This is our simple helper function. '''
        html = '<span>Hello (PublicaMundi) World</span>'
        return p.toolkit.literal(html)

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
    def debug_template_vars(cls, debug_info):
        ''' A debug helper similar to h.debug_full_info_as_list '''
        out = {}
        ignored_keys = [
            'c', 'app_globals', 'g', 'h', 'request', 'tmpl_context', 'actions', 'translator', 'session', 'N_', 'ungettext', 'config', 'response', '_']
        ignored_context_keys = [
            '__class__', '__context', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__',
            '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
            '__weakref__', 'action', 'environ', 'pylons', 'start_response', 'userobj', 'page']

        debug_vars = debug_info['vars']

        for key in filter(lambda k: not k in ignored_keys, debug_vars.keys()):
            out[key] = debug_vars[key]

        if 'tmpl_context' in debug_vars:
            for key in filter(lambda k: not k in ignored_context_keys, debug_info['c_vars']):
                val = getattr(debug_vars['tmpl_context'], key)
                if hasattr(val, '__call__'):
                    val = repr(val)
                out['c.%s' % key] = val

        return out

    @classmethod
    def dump_jsonpickle(cls, obj):
        return jsonpickle.encode(obj)

    ## ITemplateHelpers interface ##

    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            # define externsion-specific helpers
            'publicamundi_helloworld': self.publicamundi_helloworld,
            'organization_list_objects': self.organization_list_objects,
            'organization_dict_objects': self.organization_dict_objects,
            # define debug helpers
            'debug_template_vars': self.debug_template_vars,
            'dump_jsonpickle': self.dump_jsonpickle,
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
        ''' Override CKAN's create/update schema '''

        from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

        def baz_converter_1(key, data, errors, context):
            ''' Some typical behaviour inside a validator/converter '''

            ## Stop processing on this key and signal the validator with another error (an instance of Invalid) 
            #raise Invalid('The baz value (%s) is invalid' %(data.get(key,'<none>')))

            ## Stop further processing on this key, but not an error
            #raise StopOnError
            pass
        
        def after_validation_processor(key, data, errors, context):
            assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
            pass
        
        def before_validation_processor(key, data, errors, context):
            assert key[0] == '__before', 'This validator can only be invoked in the __before stage'
            pass

        # Update default validation schema (inherited from DefaultDatasetForm)

        schema.update({
            'foo': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('foo'),
            ],
            'baz': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras'),
                baz_converter_1,
            ],
        })

        # Add callbacks to the '__after' pseudo-key to be invoked after all key-based validators/converters

        if not schema.get('__after'):
            schema['__after'] = []
        schema['__after'].append(after_validation_processor)

        # A similar hook is also provided by the '__before' pseudo-key with obvious functionality.

        if not schema.get('__before'):
            schema['__before'] = []
        # any additional validator must be inserted before the default 'ignore' one. 
        schema['__before'].insert(-1, before_validation_processor) # insert as second-to-last

        return schema

    def create_package_schema(self):
        schema = super(DatasetForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(DatasetForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(DatasetForm, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        schema.update({
            'foo': [
                toolkit.get_converter('convert_from_tags')('foo'),
                toolkit.get_validator('ignore_missing')
            ],
            'baz': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
        })

        return schema

    def setup_template_variables(self, context, data_dict):
        ''' Setup (add/modify/hide) variables to feed the template engine.
        This is done through through toolkit.c (template thread-local context object).
        '''
        super(DatasetForm, self).setup_template_variables(context, data_dict)
        c = toolkit.c
        c.publicamundi_magic_number = 99

    # Note for all *_template hooks: 
    # We choose not to modify the path for each template (so we simply call the super() method). 
    # If a specific template's behaviour needs to be overriden, this can be done by means of 
    # template inheritance (e.g. Jinja2 `extends' or CKAN `ckan_extends')

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
        (Note that the create method will return a package domain object, which may not include all fields).
        Also the newly created package id will be added to the dict.
        At this point the package is possibly in 'draft' state so most action-api calls should fail.
        But, we can interact with the object model (through typical ORM) to modify package's properties.
        '''
        #raise Exception('Breakpoint')
        log1.info('A package has been created: %s', pkg_dict)
        pass

    def after_update(self, context, pkg_dict):
        '''
        Extensions will receive the validated data dict after the package has been updated
        (Note that the edit method will return a package domain object, which may not include all fields).
        '''
        #raise Exception('Breakpoint')
        log1.info('A package has been updated: context=%r %s', context, pkg_dict)
        pass

    def after_delete(self, context, pkg_dict):
        '''
        Extensions will receive the data dict (typically containing just the package id) after the package has been deleted.
        '''
        log1.info('A package has been deleted: %s', pkg_dict)
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

