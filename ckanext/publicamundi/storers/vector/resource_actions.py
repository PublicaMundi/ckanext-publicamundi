import json
from pylons import config

import ckan.model as model
from ckan.model.types import make_uuid
import ckan.plugins.toolkit as toolkit
from ckan.lib.celery_app import celery
import ckan.lib.helpers as h
from ckan.lib.dictization.model_dictize import resource_dictize

from ckanext.publicamundi.model.resource_ingest import (
    ResourceIngest, ResourceStorerType, IngestStatus)
from ckanext.publicamundi.storers.vector.resources import (
    DBTableResource, WMSResource)

def _get_site_url():
    try:
        return h.url_for_static('/', qualified=True)
    except AttributeError:
        return config.get('ckan.site_url', '')

def _get_site_user():
    user = toolkit.get_action('get_site_user')({
        'model': model,
        'ignore_auth': True,
        'defer_commit': True
    }, {})
    return user

def _make_default_context():
    '''Make a default (base) context for created Celery tasks
    '''

    user = _get_site_user()
    return {
        'site_url': _get_site_url(),
        # User on behalf of which a task is executed
        'user_name': user['name'],
        'user_api_key': user['apikey'],
        # Configuration needed to setup vectorstorer
        'gdal_folder': config.get(
            'ckanext.publicamundi.vectorstorer.gdal_folder'),
        'temp_folder': config.get(
            'ckanext.publicamundi.vectorstorer.temp_dir'),
    }

def identify_resource(resource):

    # With resource_dictize we get the correct resource url
    # even if dataset is in draft state

    task_id = make_uuid()

    resource_dict = resource_dictize(resource, {'model': model})
    context = _make_default_context()
    celery.send_task(
        'vectorstorer.identify',
        args=[resource_dict, context],
        countdown=15,
        task_id=task_id)

    res_identify = model.Session.query(ResourceIngest).filter(
        ResourceIngest.resource_id == resource.id).first()
    if res_identify:
        # This is when a user had previously rejected the ingestion workflow, 
        # but now wants to re-identify the resource
        model.Session.delete(res_identify)
        new_res_identify = ResourceIngest(
            task_id,
            resource.id,
            ResourceStorerType.VECTOR)
        model.Session.add(new_res_identify)
        model.Session.commit()
    else:
        # A newly created/updated resource needs to be identified
        new_res_identify = ResourceIngest(
            task_id,
            resource.id,
            ResourceStorerType.VECTOR)
        model.Session.add(new_res_identify)

def _make_geoserver_context():
    return {
        'geoserver_url':
            config['ckanext.publicamundi.vectorstorer.geoserver_url'].rstrip('/'),
        'geoserver_workspace':
            config['ckanext.publicamundi.vectorstorer.geoserver_workspace'],
        'geoserver_admin':
            config['ckanext.publicamundi.vectorstorer.geoserver_admin'],
        'geoserver_password':
            config['ckanext.publicamundi.vectorstorer.geoserver_password'],
        'geoserver_ckan_datastore':
            config['ckanext.publicamundi.vectorstorer.geoserver_ckan_datastore']
    }

def create_ingest_resource(resource, layer_params):
    package_id = resource.as_dict()['package_id']
    context = _make_default_context()
    context.update({
        'package_id': package_id,
        'db_params': config['ckan.datastore.write_url'],
        'layer_params': layer_params
    })
    geoserver_context = _make_geoserver_context()
    resource_dict = resource_dictize(resource, {'model': model})
    task_id = make_uuid()
    celery.send_task(
        'vectorstorer.upload',
        args=[resource_dict, context, geoserver_context],
        task_id=task_id)

    res_ingest = model.Session.query(ResourceIngest).filter(
        ResourceIngest.resource_id == resource.id).first()
    res_ingest.status = IngestStatus.PUBLISHED
    res_ingest.celery_task_id = task_id
    model.Session.commit()

def update_ingest_resource(resource):
    package_id = resource.as_dict()['package_id']
    resource_list_to_delete = _get_child_resources(resource.as_dict())
    context = _make_default_context()
    context.update({
        'resource_list_to_delete': resource_list_to_delete,
        'package_id': package_id,
        'db_params': config['ckan.datastore.write_url'],
    })
    geoserver_context = _make_geoserver_context()
    resource_dict = resource_dictize(resource, {'model': model})
    task_id = make_uuid()
    celery.send_task(
        'vectorstorer.update',
        args=[resource_dict, context, geoserver_context],
        task_id=task_id)

def delete_ingest_resource(resource, pkg_delete=False):
    resource_dict = resource_dictize(resource, {'model': model})
    resource_list_to_delete = None
    if ((resource_dict['format'] == WMSResource.FORMAT or
            resource_dict['format'] == DBTableResource.FORMAT) and
            'vectorstorer_resource' in resource_dict):
        if pkg_delete:
            resource_list_to_delete = _get_child_resources(resource)
    else:
        resource_list_to_delete = _get_child_resources(resource)
    context = _make_default_context()
    context.update({
        'resource_list_to_delete': resource_list_to_delete,
        'db_params': config['ckan.datastore.write_url']
    })
    geoserver_context = _make_geoserver_context()
    task_id = make_uuid()
    celery.send_task(
        'vectorstorer.delete',
        args=[resource_dict, context, geoserver_context],
        task_id=task_id)

    if 'vectorstorer_resource' in resource and not pkg_delete:
        _delete_child_resources(resource)

def _delete_child_resources(parent_resource):
    user = _get_site_user()
    action_context = {'model': model, 'user': user.get('name')}
    current_package = toolkit.get_action('package_show')(
        action_context, {'id': parent_resource['package_id']})
    resources = current_package['resources']
    for child_resource in resources:
        if 'parent_resource_id' in child_resource:
            if child_resource['parent_resource_id'] == parent_resource['id']:
                action_result = toolkit.get_action('resource_delete')(
                    action_context, {'id': child_resource['id']})
    return

def _get_child_resources(parent_resource):
    child_resources = []
    user = _get_site_user()
    action_context = {'model': model, 'user': user.get('name')}
    current_package = toolkit.get_action('package_show')(
        action_context, {'id': parent_resource['package_id']})
    resources = current_package['resources']
    for child_resource in resources:
        if 'parent_resource_id' in child_resource:
            if child_resource['parent_resource_id'] == parent_resource['id']:
                child_resources.append(child_resource['id'])
    return child_resources

def delete_ingest_resources_in_package(package):
    user = _get_site_user()
    context = {'model': model,
               'session': model.Session,
               'user': user.get('name')}
    resources = package['resources']
    for res in resources:
        if ('vectorstorer_resource' in res and 
                res['format'] == DBTableResource.FORMAT):
            res['package_id'] = package['id']
            delete_ingest_resource(res, True)
