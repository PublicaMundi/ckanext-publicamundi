from ckan.lib.base import (c, redirect, BaseController, render, abort)

import pylons.config as config
from ckan.lib import helpers
import ckan.plugins.toolkit as toolkit

_ = toolkit._
NotFound = toolkit.ObjectNotFound
NotAuthorized = toolkit.NotAuthorized

class PackageController(BaseController):
    def package_apis(self, id):
        pkg_dict = self._check_access(action='package_show', id=id)
        c.pkg_dict = pkg_dict

        return render('package/developers.html')

    #def preview_openlayers(self, id, resource_id):
    #    pkg_dict = self._check_access(action='package_show', id=id)
    #    res_dict = self._check_access(action='resource_show', id=resource_id)
    #    c.pkg_dict = pkg_dict
    #    c.res = res_dict
    #    return render ('package/snippets/openlayers.html')

    def _check_access(self, action, id):
        context = self._get_context()
        data_dict = {'id': id }
        try:
            pkg_dict = toolkit.get_action(action)(context, data_dict)
            return pkg_dict
        except NotFound:
            abort(404, _('Not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

    def _get_context(self):
        context = {
            'for_view': True,
            'user': c.user or c.author,
        }
        return context
