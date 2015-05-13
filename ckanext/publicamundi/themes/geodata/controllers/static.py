from ckan.lib.base import (redirect, BaseController, render)

import pylons.config as config
from ckan.lib import helpers
import ckan.plugins.toolkit as toolkit

class Controller(BaseController):
    def redirect_news(self):
        locale = helpers.lang()
        #return('/news?lang=el')
        wp_url = config.get('ckanext.publicamundi.themes.geodata.wordpress_url')

        if wp_url:
            redirect(wp_url+'?lang={0}'.format(locale))
        else:
            redirect('/')
        #redirect('/news?lang={0}'.format(locale))
    def developers(self):
        return render('developers/index.html')

    def redirect_maps(self):
        base_url = config.get('ckan.site_url')
        maps_url = config.get('ckanext.publicamundi.themes.geodata.maps_url')
        if base_url and maps_url:
            redirect(base_url+maps_url)
