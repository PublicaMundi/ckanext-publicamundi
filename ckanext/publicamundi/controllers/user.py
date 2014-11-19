from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
from pylons import url
from pylons.controllers.util import redirect
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.common import _
import ckan
import json
from ckanext.publicamundi.model.resource_identify import ResourceIdentify,TaskNotReady,TaskFailed,IdentifyStatus,ResourceTypes
from ckanext.publicamundi.lib import identification_helper
from ckan.lib.base import c
from ckanext.publicamundi.storers.vector import resource_actions
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

class UserController(BaseController):
 
    
    def dashboard_resources(self):
	user_dict = self._check_access() 
        self._setup_template_variables(user_dict)
        return render('user/dashboard_resources.html')
    
    def admin_page_resources(self):
        user_dict = self._check_access() 
        self._setup_template_variables(user_dict)
        return render('user/admin_page_resources.html')
    
    def _check_access(self):
	context,data_dict = self._get_context()
	try:
            user_dict = toolkit.get_action('user_show')(context, data_dict)
            return user_dict
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))
    def _get_context(self):
	context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}
        return context,data_dict
        
    def _setup_template_variables(self,user_dict ):
        c.is_sysadmin = False
        
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

    def reject(self, resource_id, parent):

	user_dict = self._check_access() 
        self._setup_template_variables(user_dict)
        
	res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id).first()
	res_identify_query.set_identify_status(IdentifyStatus.REJECTED)
	ckan.model.Session.commit()
	if parent=='dashboard':
	    _action='dashboard_resources'
	else:
	    _action='admin_page_resources'
	redirect(url(controller='ckanext.publicamundi.controllers.user:UserController', action=_action))
    
    def identify(self,resource_id,resource_type, parent):
	user_dict = self._check_access() 
        self._setup_template_variables(user_dict)
        context,data_dict = self._get_context()
	resource = logic.get_action('resource_show')(context,{'id': resource_id})
	if resource_type == ResourceTypes.VECTOR:
	    resource_actions.identify_resource(resource)
	
	if parent=='dashboard':
	    _action='dashboard_resources'
	else:
	    _action='admin_page_resources'
	redirect(url(controller='ckanext.publicamundi.controllers.user:UserController', action=_action))
	
    def render_ingestion_template(self,resource_id):
	c.resource_id = resource_id
	c.task_result = json.loads(identification_helper.identify(resource_id)['result'])
	res_identify_obj = ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id).first()
	if res_identify_obj.get_resource_type()==ResourceTypes.VECTOR:
	    return render('user/snippets/ingest_templates/vector/vector.html')