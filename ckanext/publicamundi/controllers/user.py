from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)
from pylons import url
from pylons.controllers.util import redirect
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.common import _
import ckan

from ckanext.publicamundi.model.resource_identify import ResourceIdentify,TaskNotReady,TaskFailed,IdentifyStatus,ResourceTypes
from ckanext.vectorstorer import resource_actions
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

class UserController(BaseController):
 
    
    def dashboard_resources(self):
	 
        context,data_dict = self._get_context()
        self._setup_template_variables(context, data_dict)
        return render('user/dashboard_resources.html')
    
    def _get_context(self):
	context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}
        return context,data_dict
        
    def _setup_template_variables(self, context, data_dict):
        c.is_sysadmin = False
        try:
            user_dict = toolkit.get_action('user_show')(context, data_dict)
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

    def reject(self,resource_id):
	context,data_dict = self._get_context()
	self._setup_template_variables(context, data_dict)
	res_identify_query=ckan.model.Session.query(ResourceIdentify).filter(ResourceIdentify.resource_id==resource_id).first()
	res_identify_query.set_identify_status(IdentifyStatus.REJECTED)
	ckan.model.Session.commit()
        redirect(url(controller='ckanext.publicamundi.controllers.user:UserController', action='dashboard_resources'))
    
    def identify(self,resource_id,resource_type):
	context,data_dict = self._get_context()
	#self._setup_template_variables(context, data_dict)
	resource = logic.get_action('resource_show')(context,{'id': resource_id})
	if resource_type == ResourceTypes.VECTOR:
	    resource_actions.identify_resource(resource)
	redirect(url(controller='ckanext.publicamundi.controllers.user:UserController', action='dashboard_resources'))