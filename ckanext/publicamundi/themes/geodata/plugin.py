import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import c
from ckan.lib.helpers import render_datetime

def most_recent_datasets(limit=10):
    datasets = toolkit.get_action('package_search')(
        data_dict={'sort': 'metadata_modified desc', 'rows':8})
    return datasets

def list_menu_items (limit=21):
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'name desc', 'all_fields':True})
    groups = groups[:limit]
    c.groups = groups

    return groups

def friendly_date(date_str):
    return render_datetime(date_str, '%d, %B, %Y')


_feedback_form = None

def feedback_form():
    return _feedback_form

class GeodataThemePlugin(plugins.SingletonPlugin):
    '''Theme plugin for geodata.gov.gr.
    '''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    
    # ITemplateHelpers
    

    def get_helpers(self):
        return {
            'newest_datasets': most_recent_datasets,
            'list_menu_items': list_menu_items,
            'friendly_date': friendly_date,
            'feedback_form': feedback_form,
        }
    
    # IConfigurer
    
    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public', 'ckanext-publicamundi-geodata-theme')

    # IConfigurable

    def configure(self, config):
        '''Pass configuration to plugins and extensions'''

        global _feedback_form
        _feedback_form = config.get('ckanext.publicamundi.themes.geodata.feedback_form')
        return

    # IRoutes

    def before_map(self, mapper):
        mapper.connect('maps', '/maps') 
        mapper.connect('developers', '/developers') 
        mapper.connect('news', '/news', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='redirect_news' )

        return mapper

    # IPackageController
    def before_view(self, pkg_dict):
        list_menu_items()
        return pkg_dict

