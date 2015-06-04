import json
from urllib import urlencode

from pylons import config

import ckan.model as model
from ckan.lib.base import (
    c, BaseController, render, request, abort, redirect)
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
accepted_sortings = ["status", "storer_type"]


class UserController(BaseController):

    def show_dashboard_resources(self):
        user_dict = self._check_access()
        user_dict = self._filter_user_dict(user_dict)
        user_dict = self._filter_deleted(user_dict)
        self._setup_template_variables(user_dict)
        return render('user/dashboard_resources.html')

    def show_admin_page_resources(self):
        user_dict = self._check_access()
        user_dict = self._filter_user_dict(user_dict)
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

    def _filter_deleted(self, user_dict):
        datasets = user_dict['datasets']
        filtered = []
        for dataset in datasets:
            if not dataset.get('state') == 'deleted':
                filtered.append(dataset)
        user_dict.update({'datasets':filtered})
        return user_dict

    def _filter_user_dict(self, user_dict):
        datasets_dict = user_dict['datasets']
        filtered_datasets_dict = []
        for dataset in datasets_dict:
            resources = dataset['resources']
            params = request.params
            filtered_resources = resources
            for param in params:

                if param in accepted_sortings:
                    filtered_resources = self._filter_resources_by_status(
                        filtered_resources, param)

            dataset['resources'] = filtered_resources
            if len(filtered_resources)>0:
                filtered_datasets_dict.append(dataset)
        user_dict['datasets'] = filtered_datasets_dict

        return user_dict

    def _filter_resources_by_status(self, resources_dict, sorting):
        filtered_resources = []
        for resource in resources_dict:
                res_ingestion = resource_ingestion.get_result(
                    resource["id"])
                #res_ingestion = {'found':True, 'status':'published', 'storer_type':'raster'}
                if res_ingestion["found"]:
                    if sorting == accepted_sortings[0]:
                        if res_ingestion["status"] == request.params.get(
                                sorting).lower():
                            filtered_resources.append(resource)
                    elif sorting == accepted_sortings[1]:
                        if res_ingestion["storer_type"] == request.params.get(
                                sorting).lower():
                            filtered_resources.append(resource)
        return filtered_resources

    def _setup_template_variables(self, user_dict):
        def search_url(params):
            url = h.url_for(controller='ckanext.publicamundi.controllers.user:UserController', action='show_dashboard_resources')
            return url_with_params(url, params)

        def url_with_params(url, params):
            params = _encode_params(params)
            return url + u'?' + urlencode(params)

        def _encode_params(params):
            return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
                    for k, v in params]

        def pager_url(q=None, page=None):
            params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

        #Resources page items
        _resources_page_items = int(config.get('ckanext.publicamundi.dashboard.resources_page_items', 1))
        # datasets paging
        c.page = h.Page(
            collection=user_dict['datasets'],
            page=request.params.get('page', 1),
            url=pager_url,
            items_per_page=_resources_page_items
        )
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
