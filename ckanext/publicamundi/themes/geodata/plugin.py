import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib import helpers
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
_maps_url = None
_news_url = None

def feedback_form():
    return _feedback_form

def get_maps_url():
    if _maps_url:
        return _maps_url
    else:
        return '/'

def get_news_url():
    locale = helpers.lang()
    if _news_url:
        return(_news_url+'?lang={0}'.format(locale))
    else:
        return '/'

def friendly_name(name):
    max_chars = 15
    if len(name) > max_chars:
        friendly_name = name.split(" ")[0]
        if len(friendly_name)+3 >= max_chars:
            friendly_name = friendly_name[:max_chars-4] + "..."
    else:
        friendly_name = name

    return friendly_name

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
            'friendly_name': friendly_name,
            'feedback_form': feedback_form,
            'get_news_url': get_news_url,
            'get_maps_url': get_maps_url,
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

        global _feedback_form, _news_url, _maps_url

        _feedback_form = config.get('ckanext.publicamundi.themes.geodata.feedback_form')
        _maps_url = config.get('ckanext.publicamundi.themes.geodata.maps_url')
        _news_url = config.get('ckanext.publicamundi.themes.geodata.news_url')

        return

    # IRoutes

    def before_map(self, mapper):
        mapper.connect('applications', '/applications', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='applications')
        #mapper.connect('maps', '/maps', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='redirect_maps' )
        #mapper.redirect('maps', 'http://http://83.212.118.10:5000/maps')
        #mapper.connect('maps', '/maps')
        #mapper.connect('news', '/news', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='redirect_news' )

        return mapper

    # IPackageController
    def before_view(self, pkg_dict):
        list_menu_items()
        return pkg_dict

