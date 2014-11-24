import codecs
import json

import ckan.model as model
from ckan.lib.base import BaseController, c, request, abort
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.storers.vector import osr
from ckanext.publicamundi.storers.vector import resource_actions

_ = toolkit._
_check_access = toolkit.check_access
_get_action = toolkit.get_action


class VectorController(BaseController):
    '''Store vector data under postgis, publish at geoserver
    '''

    def _make_default_context(self):
        return {
            'model': model,
            'session': model.Session,
            'user': c.user,
        }
    
    def ingest(self, resource_id):
        
        # Check if authorized to update

        context = self._make_default_context()
        try:
            _check_access('resource_update', context, dict(id=resource_id))
        except toolkit.ObjectNotFound as ex:
            abort(404)
        except toolkit.NotAuthorized as ex:
            abort(403, _('Not authorized to update resource'))
            
        # Read layer opts, procceed to ingestion

        layer_options = json.loads(request.params.get('data'))

        resource = model.Session.query(model.Resource).get(resource_id)
        resource_actions.create_ingest_resource(resource, layer_options)

    def _get_encoding(self):
        _encoding = request.params.get('encoding', u'utf-8')

        if len(_encoding) == 0:
            _encoding = u'utf-8'
            return _encoding

        else:
            if self._encoding_exists(_encoding):
                return _encoding
            else:
                abort(400, _('Bad Encoding : %s') % _encoding)

    def _encoding_exists(self, encoding):
        try:
            codecs.lookup(encoding)
        except LookupError:
            return False
        return True

    def _get_projection(self):
        proj_param = request.params.get('projection')
        if not proj_param:
            return None
        try:

            _projection = int(proj_param)
            _spatial_ref = osr.SpatialReference()
            _spatial_ref.ImportFromEPSG(_projection)
            return _projection
        except ValueError:
            abort(400, _('Bad EPSG code : %s') % proj_param)
        except RuntimeError:
            abort(400, _('Bad EPSG code : %s') % proj_param)
        except OverflowError:
            abort(400, _('Bad EPSG code : %s') % proj_param)

    def _get_geometry_params(self):

        _geometry_column_param = request.params.get('geometry_column', u'')
        _geometry_type_param = request.params.get('geometry_type', u'')

        _geometry_type = None
        _geometry_column = None

        if _geometry_type_param.upper() in ['WKT', 'XY', 'YX', 'XYZ']:
            _geometry_type = _geometry_type_param

        if len(_geometry_column_param) == 0:
            _geometry_column = None

        return _geometry_column, _geometry_type
