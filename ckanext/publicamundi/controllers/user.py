from ckan.lib.base import (c, request, response)
from ckan.lib.base import (BaseController, render, abort, redirect)

import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.helpers as h

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

class UserController(BaseController):
 
    
    def dashboard_resources(self):
	context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}
        self._setup_template_variables(context, data_dict)
        return render('user/dashboard_resources.html')
    
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