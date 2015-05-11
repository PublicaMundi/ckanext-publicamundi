from ckan.lib.base import (redirect, BaseController, render)

from ckan.lib import helpers
import pylons.config as config

class Controller(BaseController):
    def redirect_news(self):
        locale = helpers.lang()
        #return('/news?lang=el')
        base_url = config.get('ckanext.publicamundi.themes.geodata.wordpress_url')

        redirect(base_url+'?lang={0}'.format(locale))
        #redirect('/news?lang={0}'.format(locale))

