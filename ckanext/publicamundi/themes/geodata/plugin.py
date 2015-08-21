import datetime
import copy
import sets

from pylons import request, config

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.datapreview as datapreview
from ckan import model
from ckan.lib import helpers, munge
from ckan.lib.base import c
from ckan.lib.helpers import render_datetime, resource_preview, url_for_static

import ckanext.publicamundi.lib.template_helpers as ext_template_helpers

def most_recent_datasets(limit=10):
    datasets = toolkit.get_action('package_search')(
        data_dict={'sort': 'metadata_modified desc', 'rows':limit})

    # Add terms for translation and call get_translation_terms
    #locale = helpers.lang()
    #translated = get_translated_dataset_groups(datasets.get('results'), locale)

    return datasets.get('results')

def list_menu_items (limit=21):
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'name desc', 'all_fields':True})
    groups = groups[:limit]
    c.groups = groups

    return groups

def friendly_date(date_str):
    return render_datetime(date_str, '%d, %B, %Y')

def get_contact_point(pkg):
    
    # If there, INSPIRE metadata take precedence
    
    if pkg.get('dataset_type') == 'inspire':
        name = pkg.get('inspire.contact.0.organization', '').decode('unicode-escape')
        email = pkg.get('inspire.contact.0.email')
    
    # If not there, use maintainer or organization info
    
    if not name:
        name = pkg.get('maintainer') or pkg['organization']['title']
    
    if not email:
        email = pkg.get('maintainer_email') or config.get('email_to')
     
    return dict(name=name, email=email)

_feedback_form_en = None
_feedback_form_el = None
_maps_url = None
_news_url = None

def feedback_form():
    locale = helpers.lang()
    if locale == 'el':
        return _feedback_form_el
    else:
        return _feedback_form_en

def get_maps_url(package_id=None, resource_id=None):
    locale = helpers.lang()
    if _maps_url:
        if package_id and resource_id:
            return('{0}?package={1}&resource={2}&locale={3}'.format(_maps_url, package_id, resource_id, locale))
        else:
            return('{0}?locale={1}'.format(_maps_url, locale))
    else:
        return '/'

def redirect_wp(page):
    locale = helpers.lang()
    if page:
        if locale == 'el':
            return('/content/{0}/'.format(page))
        else:
            return('/content/{0}-{1}/'.format(page, locale))
    else:
        return('/content/')

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

#_previewable_formats = ['wms', 'wfs']
#def get_previewable_formats():
#    return _previewable_formats


# Returns the most suitable preview by checking whether ingested resources provide a better preview visualization
def preview_resource_or_ingested(pkg, res):
    snippet = resource_preview(res, pkg)
    data_dict = copy.copy(pkg)
    data_dict.update({'resource':res})

    if not _resource_preview(data_dict):
        raster_resources = ext_template_helpers.get_ingested_raster(pkg,res)
        vector_resources = ext_template_helpers.get_ingested_vector(pkg,res)

        for ing_res in raster_resources:
        #for ing_res in pkg.get('resources'):
            data_dict.update({'resource':ing_res})
            if _resource_preview(data_dict):
                snippet = resource_preview(ing_res, pkg)
                break
        for ing_res in vector_resources:
            data_dict.update({'resource':ing_res})
            if _resource_preview(data_dict):
                snippet = resource_preview(ing_res, pkg)
                break
    return snippet

def can_preview_resource_or_ingested(pkg, res):
    previewable = res.get('can_be_previewed')
    if not previewable:
        raster_resources = ext_template_helpers.get_ingested_raster(pkg,res)
        vector_resources = ext_template_helpers.get_ingested_vector(pkg,res)

        for ing_res in raster_resources:
        #for ing_res in pkg.get('resources'):
            if ing_res.get('can_be_previewed'):
                previewable = True
                break
        for ing_res in vector_resources:
            if ing_res.get('can_be_previewed'):
                previewable = True
                break
    return previewable

def _resource_preview(data_dict):
    return bool(datapreview.res_format(data_dict['resource'])
                    in datapreview.direct() + datapreview.loadable()
                    or datapreview.get_preview_plugin(
                        data_dict, return_first=True))

def get_translated_dataset_groups(datasets):
    desired_lang_code = helpers.lang()
    terms = sets.Set()
    for dataset in datasets:
        groups = dataset.get('groups')
        organization = dataset.get('organization')
        if groups:
            terms.add(groups[0].get('title'))
        if organization:
            terms.add(organization.get('title'))
    # Look up translations for all datasets in one db query.
    translations = toolkit.get_action('term_translation_show')(
        {'model': model},
        {'terms': terms,
            'lang_codes': (desired_lang_code)})

    for dataset in datasets:
        groups = dataset.get('groups')
        organization = dataset.get('organization')
        items = []
        if groups:
            items.append(groups[0])
        if organization:
            items.append(organization)
        for item in items:
            matching_translations = [translation for
                    translation in translations
                    if translation['term'] == item.get('title')
                    and translation['lang_code'] == desired_lang_code]
            if matching_translations:
                assert len(matching_translations) == 1
                item['title'] = (
                        matching_translations[0]['term_translation'])
    return datasets

# Helper function to ask for specific term to be translated
def get_term_translation(term):
    desired_lang_code = helpers.lang()
    translations = toolkit.get_action('term_translation_show')(
        {'model': model},
        {'terms': term,
            'lang_codes': (desired_lang_code)})
    matching_translations = [translation for
                    translation in translations
                    if translation['term'] == term
                    and translation['lang_code'] == desired_lang_code]
    if matching_translations:
        assert len(matching_translations) == 1
        term = (
                matching_translations[0]['term_translation'])
    return term

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
            'redirect_wp': redirect_wp,
            'get_news_url': get_news_url,
            'get_maps_url': get_maps_url,
            'preview_resource_or_ingested': preview_resource_or_ingested,
            'can_preview_resource_or_ingested': can_preview_resource_or_ingested,
            'get_translated_dataset_groups' : get_translated_dataset_groups,
            'get_term_translation': get_term_translation,
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

        global _feedback_form_en, _feedback_form_el, _news_url, _maps_url

        _feedback_form_en = config.get('ckanext.publicamundi.themes.geodata.feedback_form_en')
        _feedback_form_el = config.get('ckanext.publicamundi.themes.geodata.feedback_form_el')
        _maps_url = config.get('ckanext.publicamundi.themes.geodata.maps_url')
        _news_url = config.get('ckanext.publicamundi.themes.geodata.news_url')
        return

    # IRoutes

    def before_map(self, mapper):
        mapper.connect('dataset_apis', '/dataset/developers/{id}', controller= 'ckanext.publicamundi.themes.geodata.controllers.package:PackageController', action='package_apis')
        mapper.connect('dataset_contact_form', '/dataset/contact/{id}', controller= 'ckanext.publicamundi.themes.geodata.controllers.contact:Controller', action='contact_form')
        #mapper.connect('preview_openlayers', '/preview_openlayers/{id}/{resource_id}', controller= 'ckanext.publicamundi.themes.geodata.controllers.package:PackageController', action='preview_openlayers')
        mapper.connect('applications', '/applications', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='applications')
        mapper.connect('send_email', '/publicamundi/util/send_email', controller= 'ckanext.publicamundi.themes.geodata.controllers.contact:Controller', action='send_email')
        mapper.connect('generate_captcha', '/publicamundi/util/generate_captcha', controller= 'ckanext.publicamundi.themes.geodata.controllers.contact:Controller', action='generate_captcha')
        #mapper.connect('maps', '/maps', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='redirect_maps' )
        #mapper.redirect('maps', 'http://http://83.212.118.10:5000/maps')
        #mapper.connect('maps', '/maps')
        #mapper.connect('news', '/news', controller= 'ckanext.publicamundi.themes.geodata.controllers.static:Controller', action='redirect_news' )

        return mapper

    # IPackageController
    def before_view(self, pkg_dict):
        list_menu_items()
        return pkg_dict

    # IPackageController 
    # this has been moved here from ckanext/multilingual MultilingualDataset
    def after_search(self, search_results, search_params):

        # Translte the unselected search facets.
        facets = search_results.get('search_facets')
        if not facets:
            return search_results

        desired_lang_code = request.environ['CKAN_LANG']
        fallback_lang_code = config.get('ckan.locale_default', 'en')

        # Look up translations for all of the facets in one db query.
        terms = sets.Set()
        for facet in facets.values():
            for item in facet['items']:
                terms.add(item['display_name'])
        translations = toolkit.get_action('term_translation_show')(
                {'model': model},
                {'terms': terms,
                    #'lang_codes': (desired_lang_code, fallback_lang_code)})
                    'lang_codes': (desired_lang_code)})

        # Replace facet display names with translated ones.
        for facet in facets.values():
            for item in facet['items']:
                matching_translations = [translation for
                        translation in translations
                        if translation['term'] == item['display_name']
                        and translation['lang_code'] == desired_lang_code]
                if not matching_translations:
                    matching_translations = [translation for
                            translation in translations
                            if translation['term'] == item['display_name']
                            and translation['lang_code'] == fallback_lang_code]
                if matching_translations:
                    assert len(matching_translations) == 1
                    item['display_name'] = (
                        matching_translations[0]['term_translation'])

        return search_results



