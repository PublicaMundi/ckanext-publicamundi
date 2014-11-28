import os
from xml.dom import minidom
from pylons import config
from geoserver.catalog import Catalog
from geoserver.catalog import UploadError

from ckan.lib.base import(
    BaseController, c, request, session, render, config, abort)
import ckan.model as model
import ckan.plugins.toolkit as toolkit

_ = toolkit._
_check_access = toolkit.check_access
_get_action = toolkit.get_action


class StyleController(BaseController):

    def _get_catalog(self):
        '''Get a configured geoserver.catalog.Catalog client instance.
        '''

        geoserver_url = config['ckanext.publicamundi.vectorstorer.geoserver_url']
        username = config['ckanext.publicamundi.vectorstorer.geoserver_admin']
        password = config['ckanext.publicamundi.vectorstorer.geoserver_password']
        catalog1 = Catalog(
            geoserver_url + "/rest", username=username, password=password)
        return catalog1
    
    def upload_sld(self, id, resource_id, operation):
        if operation:
            self._get_context(id, resource_id)
            if operation.lower() == 'show':
                pass
            elif operation.lower() == 'upload':
                sld_file_param = request.POST['sld_file']
                try:
                    file_extension = os.path.splitext(
                        sld_file_param.filename)[1]
                    if file_extension.lower() == ".xml":
                        sld_file = sld_file_param.file
                        c.sld_body = sld_file.read()
                    else:
                        raise AttributeError
                except AttributeError:
                    c.error = 'No XML file was selected.'
            elif operation.lower() == 'submit':
                sld_body = request.POST['sld_body']
                self._submit_sld(sld_body)
            return render('style/upload_sld_form.html')
        else:
            abort(404, _('Resource not found'))

    def edit_current_sld(self, id, resource_id, operation):
        if operation:
            self._get_context(id, resource_id)
            if operation.lower() == 'show':
                c.sld_body = self._get_layer_style(resource_id)
            elif operation.lower() == 'submit':
                sld_body = request.POST['sld_body']
                self._submit_sld(sld_body)
            return render('style/edit_sld_form.html')
        else:
            abort(404, _('Resource not found'))

    def _get_layer_style(self, resource_id):
        cat = self._get_catalog()
        layer = cat.get_layer(c.layer_id)
        default_style = layer._get_default_style()
        xml = minidom.parseString(default_style.sld_body)
        return xml.toprettyxml()

    # Fixme: The following method is not doing what its name says.
    # Separate authorization checks from context retrieval.
    def _get_context(self, id, resource_id):
        
        context = {
            'model': model, 'session': model.Session, 'user': c.user}
        try:
            _check_access('package_update', context, {'id': id})
            c.resource = _get_action('resource_show')(context, {'id': resource_id})
            c.package = _get_action('package_show')(context, {'id': id})
            c.pkg = context['package']
            c.pkg_dict = c.package
            if 'vectorstorer_resource' in c.resource and c.resource[
                    'format'].lower() == 'wms':
                c.layer_id = c.resource['parent_resource_id']
            else:
                abort(400, _('Resource is not a vectorstorer WMS resource'))
        except toolkit.ObjectNotFound:
            abort(404, _('Resource not found'))
        except toolkit.NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

    def _submit_sld(self, sld_body):
        cat = self._get_catalog()
        try:
            layer = cat.get_layer(c.layer_id)
            default_style = layer._get_default_style()
            if default_style.name == c.layer_id:
                cat.create_style(default_style.name, sld_body, overwrite=True)
            else:
                cat.create_style(c.layer_id, sld_body, overwrite=True)
                layer._set_default_style(c.layer_id)
                cat.save(layer)
            c.success = True
        except UploadError as e:
            c.sld_body = sld_body
            c.error = e
        return
