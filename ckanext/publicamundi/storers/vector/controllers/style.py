import os
from xml.dom import minidom
from pylons import config
from geoserver.catalog import Catalog
from geoserver.catalog import UploadError
import mapscript

from ckan.lib.base import(
    BaseController, c, request, session, render, config, abort)
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.storers.vector.lib import utils
_ = toolkit._
_check_access = toolkit.check_access
_get_action = toolkit.get_action


class StyleController(BaseController):

    def render_style_popup(self, id, resource_id, template):
        '''Returns a bootstrap popup (if the user has editing
        rights to the resource), where users can edit the style of a
        WMS Resource'''

        self._check_user_access(resource_id)
        self._setup_template_variables(id, resource_id)
        return render('style/main.html')

    def edit_current_sld(self, id, resource_id):
        '''Returns an xml editor, where users can edit the current
        SLD as it is produced from the publishing server'''

        self._check_user_access(resource_id)
        pkg_name, resource = self._setup_template_variables(id, resource_id)
        c.sld_body = self._get_layer_style(pkg_name, resource)
        return render('style/edit_sld_form.html')

    def upload_edited_sld(self, id, resource_id):
        '''Handles the changed SLD of a WMS Resource.'''

        self._check_user_access(resource_id)
        pkg_name, resource = self._setup_template_variables(id, resource_id)
        self._submit_sld(pkg_name, resource)
        return render('style/edit_sld_form.html')

    def _get_layer_style(self, pkg_name, resource):
        '''Returns the SLD of the WMS Layer'''
        published_at = utils.get_publishing_server(resource)
        default_style = None
        if published_at == utils.PUBLISHED_AT_GEOSERVER:
            cat = self._get_geoserver_catalog()
            layer = cat.get_layer(c.layer_id)
            default_style = layer._get_default_style().sld_body
        elif published_at == utils.PUBLISHED_AT_MAPSERVER:
            map, abs_mapfile_path = self._get_mapfile_layer(pkg_name)
            layer = map.getLayerByName(resource['wms_layer'])
            default_style = layer.generateSLD()
        xml = minidom.parseString(default_style)
        return xml.toprettyxml()

    def _submit_sld(self,pkg_name, resource):
        '''Submit the SLD to the appropriate mapping server'''

        # Find the mapping server where the WMS Layer is published
        published_at =  utils.get_publishing_server(resource)

        if published_at == utils.PUBLISHED_AT_GEOSERVER:
            self._submit_geoserver_sld()
        elif published_at == utils.PUBLISHED_AT_MAPSERVER:
            map, abs_mapfile_path = self._get_mapfile_layer(pkg_name)
            self._submit_mapserver_sld(map, resource['wms_layer'])
            map.save(abs_mapfile_path)

    def _submit_geoserver_sld(self):
        ''' Updates the SLD file of a WMS Layer in Geoserver.
        Throws Validation Errors if the SLD is not valid.'''

        sld_body = request.POST['sld_body']
        cat = self._get_geoserver_catalog()
        try:
            layer = cat.get_layer(c.layer_id)

            # Get the default style for this WMS Layer
            default_style = layer._get_default_style()

            if default_style.name == c.layer_id:
                # If the name of the default SLD is the same as the Layer ID
                # just update the current SLD
                cat.create_style(default_style.name, sld_body, overwrite=True)
            else:
                # If the name of the default SLD is not the same as the Layer ID
                # this WMS Layer uses a default Style from Geoserver. So we need
                # to create a unique SLD File for this layer and set it as default
                cat.create_style(c.layer_id, sld_body, overwrite=True)
                layer._set_default_style(c.layer_id)
                cat.save(layer)
            c.success = True
        except UploadError as e:
            # A validation Error has occured. Return the SLD as text (The one that
            # the user has modified) and display the errors.
            c.sld_body = sld_body
            c.error = e
        return

    def _submit_mapserver_sld(self, map, ss):
        ''' Updates the SLD file of a WMS Layer in Mapserver'''

        sld_body = request.POST['sld_body']
        layer = map.getLayerByName(ss)
        layer.applySLD(sld_body, ss)

    def _setup_template_variables(self, id, resource_id):
        ''' Setup template variables which are necessary for rendering
        the templates. Returns package name and resource dictionary.'''

        context = self._create_context()
        c.resource = _get_action('resource_show')(context, {'id': resource_id})
        c.pkg = _get_action('package_show')(context, {'id': id})

        # Check if the resource format is WMS and was produced from vectorstorer
        if 'vectorstorer_resource' in c.resource and c.resource[
                'format'].lower() == 'wms':
            c.layer_id = c.resource['parent_resource_id']
        else:
            abort(400, _('Resource is not a vectorstorer WMS resource'))
        return c.pkg['name'], c.resource

    def _check_user_access(self, resource_id):
        ''' Checks if the user has access in the requested resource and
        aborts if not. Also checks if the resource exists. '''

        context = self._create_context()
        try:
            _check_access('resource_update', context, {'id': resource_id})
        except toolkit.ObjectNotFound:
            abort(404, _('Resource not found'))
        except toolkit.NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

    def _create_context(self):
        ''' Create a user context to check access in resources'''
        context = {
            'model': model, 'session': model.Session, 'user': c.user}
        return context

    def _get_geoserver_catalog(self):
        '''Get a configured geoserver.catalog.Catalog client instance.
        '''

        geoserver_url = config['ckanext.publicamundi.vectorstorer.geoserver.url']
        username = config['ckanext.publicamundi.vectorstorer.geoserver.username']
        password = config['ckanext.publicamundi.vectorstorer.geoserver.password']
        catalog1 = Catalog(
            geoserver_url.rstrip('/') + "/rest", username=username, password=password)
        return catalog1

    def _get_mapfile_layer(self, dataset_name):
        '''Get the layer from the mapfile related to the dataset.
        '''
        mapfile_folder = config['ckanext.publicamundi.vectorstorer.mapserver.mapfile_folder']

        abs_mapfile_path = os.path.join(mapfile_folder, dataset_name + '.map')

        if os.path.exists(abs_mapfile_path):
            map = mapscript.mapObj(abs_mapfile_path)
            return map, abs_mapfile_path
        else:
            raise AttributeError