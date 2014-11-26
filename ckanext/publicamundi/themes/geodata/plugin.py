import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

def most_recent_datasets(limit=10):
    datasets = toolkit.get_action('package_search')(
        data_dict={'sort': 'metadata_modified desc', 'rows':8})
    return datasets

def list_menu_items (limit=16):
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'name desc', 'all_fields':True})
    groups = groups[:limit]

    return groups

def friendly_date(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f").date()
    return date.strftime('%d, %b, %Y')

global _feedback_form
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

        mapper.connect('maps', '') 
        #mapper.redirect('/dashboard', '/dashboard/datasets')

        return mapper


