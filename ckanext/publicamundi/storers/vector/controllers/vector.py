import codecs
import json
from ckan.lib.base import BaseController, c, request, abort
from ckan.logic import get_action, check_access, model, NotFound, NotAuthorized
import ckan
from pylons.controllers.util import redirect
from pylons import url
from ckan.common import _
from ckanext.publicamundi.storers.vector.settings import osr
from ckanext.publicamundi.storers.vector import resource_actions
from ckan.lib.celery_app import celery
from ckan.model.types import make_uuid
from ckan.lib.dictization.model_dictize import resource_dictize

from ckanext.publicamundi.model.resource_identify import ResourceIdentify,TaskNotReady,TaskFailed,IdentifyStatus,ResourceTypes

_check_access = check_access

class VectorController(BaseController):
    """VectorController will be used to publish vector data at postgis and geoserver"""
	
    def inject(self,resource_id):

	
	self._get_context(resource_id)
	
        encoding = self._get_encoding()
        projection = self._get_projection()    
        
        #Extra parm for csv,xls
        geometry_column, geometry_type = self._get_geometry_params() 
        
        resource=ckan.model.Session.query(model.Resource).get(resource_id)
       
	extra_params={
		      "encoding":encoding,
		      "projection":projection,
		      "geometry_type":geometry_type,
		      "geometry_column":geometry_column
		      }
	
        resource_actions.create_vector_storer_task(resource,extra_params)
        
        res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id).first()
	res_identify_query.set_identify_status(IdentifyStatus.PUBLISHED)
	ckan.model.Session.commit()
        redirect(url(controller='ckanext.publicamundi.controllers.user:UserController', action='dashboard_resources'))
    
    def reject(self,resource_id):

	resource_id = request.params.get('resource_id',u'')
	self._get_context(resource_id)
	
        encoding = self._get_encoding()
        projection = self._get_projection()    
        
        #Extra parm for csv,xls
        geometry_column, geometry_type = self._get_geometry_params() 
        
        resource=ckan.model.Session.query(model.Resource).get(resource_id)
       
	extra_params={
		      "encoding":encoding,
		      "projection":projection,
		      "geometry_type":geometry_type,
		      "geometry_column":geometry_column
		      }
	
        resource_actions.create_vector_storer_task(resource,extra_params)
        
    def _get_context(self,resource_id):
	context = {'model': model, 'session': model.Session,
                   'user': c.user}
	  
        try:
	    _check_access('resource_update',context, {'id':resource_id })
            resource = get_action('resource_show')(context,
                                                     {'id': resource_id})
	    return (resource)
            
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % resource_id)
            
            
    def _get_encoding(self):
	_encoding=request.params.get('encoding',u'utf-8')
	
	if len(_encoding)==0:
	    _encoding=u'utf-8'
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
	try:

	    proj_param=request.params.get('projection',u'')
	    _projection=int(proj_param)
	    _spatial_ref = osr.SpatialReference()
	    _spatial_ref.ImportFromEPSG(_projection)
	   
	except ValueError:
	    abort(400, _('Bad EPSG code : %s') % proj_param)
	except RuntimeError:
	    abort(400, _('Bad EPSG code : %s') % proj_param)
	except OverflowError:
	    abort(400, _('Bad EPSG code : %s') % proj_param)

    def _get_geometry_params (self):
	
	_geometry_column_param = request.params.get('geometry_column',u'')
	_geometry_type_param = request.params.get('geometry_type',u'')
	
	_geometry_type = None
	_geometry_column = None
	
	if _geometry_type_param.upper() in ['WKT','XY','YX','XYZ']:
	    _geometry_type = _geometry_type_param
	
	if len(_geometry_column_param)==0:
	    _geometry_column=None
	    
	return _geometry_column, _geometry_type