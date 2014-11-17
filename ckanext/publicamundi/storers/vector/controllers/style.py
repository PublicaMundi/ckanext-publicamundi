import os
from xml.dom import minidom
from pylons import config
from geoserver.catalog import Catalog
from ckan.lib.base import BaseController, c, g, request, \
                          response, session, render, config, abort, redirect

from geoserver.catalog import UploadError
from ckan.logic import *
from ckan.common import _
_check_access = check_access

NoFileSelected='No XML file was selected.'

class NotVectorStorerWMS(Exception):
    pass

class StyleController(BaseController):
    
    def upload_sld(self,id,resource_id,operation):
	if operation:
	    self._get_context(id,resource_id)
	    if operation.lower()=='show':
		pass
	    elif operation.lower()=='upload':
		sld_file_param = request.POST['sld_file']
		try:
                    fileExtension = os.path.splitext(sld_file_param.filename)[1]
		    if fileExtension.lower()==".xml":
			sld_file=sld_file_param.file
			c.sld_body=sld_file.read()
		    else:
		        raise AttributeError
		except AttributeError:
		   c.error=NoFileSelected
	    elif operation.lower()=='submit':
		sld_body = request.POST['sld_body']
		self._submit_sld(sld_body)
	    return render('style/upload_sld_form.html')
	else:
	    abort(404, _('Resource not found'))

    def edit_current_sld(self,id,resource_id,operation):
	if operation:
	    self._get_context(id,resource_id)
	    if operation.lower()=='show':
		c.sld_body=self._get_layer_style(resource_id)
	    elif operation.lower()=='submit':
		sld_body = request.POST['sld_body']
		self._submit_sld(sld_body)
	    return render('style/edit_sld_form.html')
	else:
	    abort(404, _('Resource not found'))
	    
    def _get_layer_style(self,resource_id):
	geoserver_url=config['ckanext-vectorstorer.geoserver_url']
	
        cat = Catalog(geoserver_url+"/rest")
	layer = cat.get_layer(c.layer_id)
	default_style=layer._get_default_style()
	xml =  minidom.parseString(default_style.sld_body)
	return xml.toprettyxml()
    
    def _get_context(self,id,resource_id):
	context = {'model': model, 'session': model.Session,
                   'user': c.user}
	  
        try:
	    _check_access('package_update',context, {'id':id })
            c.resource = get_action('resource_show')(context,
                                                     {'id': resource_id})
            c.package = get_action('package_show')(context, {'id': id})
            c.pkg = context['package']
            c.pkg_dict = c.package
            if c.resource.has_key('vectorstorer_resource') and c.resource['format'].lower()=='wms':
                   c.layer_id=c.resource['parent_resource_id']
	    else:
		raise NotVectorStorerWMS
        except NotVectorStorerWMS:
            abort(400, _('Resource is not WMS VectorStorer resource'))
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

    def _submit_sld(self,sld_body):
	try:
	    geoserver_url=config['ckanext-vectorstorer.geoserver_url']
            cat = Catalog(geoserver_url+"/rest")
	    layer = cat.get_layer(c.layer_id)
	    default_style=layer._get_default_style()
	    if default_style.name ==c.layer_id:
		cat.create_style(default_style.name, sld_body, overwrite=True)
	    else:
		cat.create_style(c.layer_id, sld_body, overwrite=True)
		layer._set_default_style(c.layer_id)
		cat.save(layer)
		
	    c.success=True
		
	except UploadError, e:
	    c.sld_body=sld_body
	    c.error=e
	    
