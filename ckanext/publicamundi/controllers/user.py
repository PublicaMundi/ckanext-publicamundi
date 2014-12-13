import json

import ckan.model as model
from ckan.lib.base import (c, BaseController, render, abort, redirect)
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.lib.helpers as h

from ckanext.publicamundi.lib import resource_ingestion
from ckanext.publicamundi.model.resource_ingest import(
    ResourceIngest, TaskNotReady, TaskFailed, IngestStatus, ResourceStorerType)
from ckanext.publicamundi.storers.vector import resource_actions # Fixme: adapt

_ = toolkit._
NotFound = toolkit.ObjectNotFound
NotAuthorized = toolkit.NotAuthorized

class UserController(BaseController):

    def show_dashboard_resources(self):
        user_dict = self._check_access()
        self._setup_template_variables(user_dict)
        return render('user/dashboard_resources.html')

    def show_admin_page_resources(self):
        user_dict = self._check_access()
        self._setup_template_variables(user_dict)
        return render('user/admin_page_resources.html')

    def _check_access(self):
        context, data_dict = self._get_context()
        try:
            user_dict = toolkit.get_action('user_show')(context, data_dict)
            return user_dict
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

    def _get_context(self):
        context = {
            'for_view': True, 
            'user': c.user or c.author,
            'auth_user_obj': c.userobj
        }
        data_dict = {'user_obj': c.userobj}
        return context, data_dict

    def _setup_template_variables(self, user_dict):
        c.is_sysadmin = False # Fixme: why? normally should be computed
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

    # Fixme: Maybe reject should be renamed (throughout this project) to ignore,
    # because in fact the original resource never gets actually rejected.

    def reject_resource(self, resource_id, parent):

        user_dict = self._check_access()
        self._setup_template_variables(user_dict)

        res_identify_query = model.Session.query(ResourceIngest).filter(
            ResourceIngest.resource_id == resource_id).first()
        res_identify_query.status = IngestStatus.REJECTED

        model.Session.commit()

        if parent == 'dashboard':
            _action = 'show_dashboard_resources'
        else:
            _action = 'show_admin_page_resources'
        redirect(toolkit.url_for(
            controller='ckanext.publicamundi.controllers.user:UserController',
            action=_action))

    def identify_resource(self, resource_id, storer_type, parent):
        user_dict = self._check_access()
        self._setup_template_variables(user_dict)
        context, data_dict = self._get_context()
        resource = model.Session.query(model.Resource).get(resource_id)
        if storer_type == ResourceStorerType.VECTOR: # Fixme: adapt
            resource_actions.identify_resource(resource)

        if parent == 'dashboard':
            _action = 'show_dashboard_resources'
        else:
            _action = 'show_admin_page_resources'
        redirect(toolkit.url_for(
            controller='ckanext.publicamundi.controllers.user:UserController',
            action=_action))

    def render_ingestion_template(self, resource_id):
        c.resource_id = resource_id
        c.task_result = resource_ingestion.get_result(resource_id)['result']
        res_identify_obj = model.Session.query(ResourceIngest).filter(
            ResourceIngest.resource_id == resource_id).first()

        if res_identify_obj.storer_type == ResourceStorerType.VECTOR: # Fixme: adapt
            return render('user/snippets/ingest_templates/vector/vector.html')
        elif res_identify_obj.storer_type == ResourceStorerType.RASTER:
            return render('user/snippets/ingest_templates/raster/raster.html')
