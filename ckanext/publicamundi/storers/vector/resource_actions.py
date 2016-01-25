import json
from pylons import config
import logging

import ckan
import ckan.model as model
from ckan.model.types import make_uuid
import ckan.plugins.toolkit as toolkit
from ckan.lib.celery_app import celery
import ckan.lib.helpers as h
from ckan.lib.dictization.model_dictize import resource_dictize

from ckanext.publicamundi.model.resource_ingest import (
    ResourceIngest, ResourceStorerType, IngestStatus)
from ckanext.publicamundi.storers.vector.resources import (
    DBTableResource, WMSResource, WFSResource)

vector_child_formats = [
    DBTableResource.FORMAT,
    WMSResource.FORMAT,
    WFSResource.FORMAT]

log = logging.getLogger(__name__)

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
    '''Returns a dictionary containg the geoserver configuration'''
    return {
        'url':
            config['ckanext.publicamundi.vectorstorer.geoserver.url'].rstrip('/'),
        'api_url':
            config['ckanext.publicamundi.vectorstorer.geoserver.api_url'].rstrip('/'),
        'reload_url':
            config.get('ckanext.publicamundi.vectorstorer.geoserver.reload_url'),
        'workspace':
            config['ckanext.publicamundi.vectorstorer.geoserver.workspace'],
        'username':
            config['ckanext.publicamundi.vectorstorer.geoserver.username'],
        'password':
            config['ckanext.publicamundi.vectorstorer.geoserver.password'],
        'datastore':
            config['ckanext.publicamundi.vectorstorer.geoserver.datastore'],
    }

def _make_mapserver_context():
    return {
        'url':
            config['ckanext.publicamundi.vectorstorer.mapserver.url'].rstrip('/'),
        'mapfile_folder':
            config['ckanext.publicamundi.vectorstorer.mapserver.mapfile_folder'],
        'templates_folder':
            config['ckanext.publicamundi.vectorstorer.mapserver.templates_folder'],
    }

def _make_backend_context():
    '''Create context for known publishing backends'''

    _geoserver_context = None
    _mapserver_context = None
    _default_publishing_server = None
    
    try:
        _geoserver_context = _make_geoserver_context()
    except KeyError:
        log.warn('Backend `geoserver` is not (properly) configured')
    else:
        _default_publishing_server = 'geoserver'
    
    try:
        _mapserver_context = _make_mapserver_context()
    except KeyError:
        log.warn('Backend `mapserver` is not (properly) configured')
    else:
        _default_publishing_server = 'mapserver'

    # If both mapserver and geoserver are found in ckan configuration check
    # for default_publishing_server vectorstorer configuration. The value of
    # this configuration must be geoserver or mapserver to decide where to
    # publish spatial resources. If this configuration is not found, use
    # geoserver as default.
    if _geoserver_context is not None and _mapserver_context is not None:
        try:
            _default_publishing_server = config['ckanext.publicamundi.vectorstorer.default_publishing_server']
        except KeyError:
            log.info('No default_publishing_server was specified, using `geoserver` as backend')
            _default_publishing_server = 'geoserver'
            pass
    
    return {
        'geoserver_context': _geoserver_context,
        'mapserver_context': _mapserver_context,
        'default_publishing_server': _default_publishing_server,
    }

def create_ingest_resource(resource, layer_params):
    package_id = resource.as_dict()['package_id']
    context = _make_default_context()
    context.update({
        'package_id': package_id,
        'db_params': config['ckan.datastore.write_url'],
        'layer_params': layer_params
    })
    backend_context = _make_backend_context()
    resource_dict = resource_dictize(resource, {'model': model})
    task_id = make_uuid()
    celery.send_task(
        'vectorstorer.upload',
        args=[resource_dict, context, backend_context],
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
    backend_context = _make_backend_context()
    resource_dict = resource_dictize(resource, {'model': model})
    task_id = make_uuid()
    celery.send_task(
        'vectorstorer.update',
        args=[resource_dict, context, backend_context],
        task_id=task_id)

def delete_ingest_resource(resource_dict):
    '''Called when a parent or child vector resource is being deleted.
    Creates a celery task that does the unpublish from Geoserver workf
    and the deletion from the database for all the resources that are
    affected from the deleted one'''

    resource_list_to_delete = None

    user = _get_site_user()
    action_context = {'model': model, 'user': user.get('name')}
    current_package = toolkit.get_action('package_show')(
        action_context, {'id': resource_dict['package_id']})
    package_resources = current_package['resources']
    
    if resource_dict['format'] in vector_child_formats:
        # Handles wms, wfs and data_table resources that have been deleted

        parent_resource = _get_parent_resource(resource_dict, package_resources)
        if parent_resource is not None:
            # If parent resource is not deleted then send the deleted resource
            # to the celery delete task with all the resources that are
            # affected from this deletion. For example if a wfs resource is
            # being deleted and the wms resource has been deleted before
            # the DBTableResource will also be deleted
            resource = resource_dict
            resource_list_to_delete = _get_resource_list_for_deletion(
                resource_dict,
                package_resources,
                parent_resource)
        else:
            # If parent resource has been deleted, vector child resources
            # will be ignored, beacause the are already unpublished from
            # Geoserver (for WMS, WFS) or deleted from database (DATA_TABLE).
            # This happens when the parent resource format is deleted and
            # all the child resources are being send to the celety delete
            # task.

            resource = None
            resource_list_to_delete = None
    else:
        # Handles parent resources (e.g Shapefile) that have been deleted
        # set the resource as None. Creates a resource list containing all
        # the resources which have as parent id the id of the resource whick
        # was deleted and their child resources. These resources firstly are
        # being unpublished from Geoserver or deleted from Database and
        # secondly they are being deleted from ckan through the resource_delete
        # api action
        resource = None
        resource_list_to_delete = _get_child_resources(resource_dict)
        for res in resource_list_to_delete:
            _chilreds=_get_child_resources(res)
            for child_res in _chilreds:
                resource_list_to_delete.append(child_res)

    # start the delete tast only if the resource list to delete
    # has at least 1 item.

    if resource_list_to_delete is not None and len(resource_list_to_delete)>0 :
        context = _make_default_context()
        context.update({
            'resource_list_to_delete': resource_list_to_delete,
            'db_params': config['ckan.datastore.write_url'],
            'package_id': resource_dict['package_id']
        })
        backend_context = _make_backend_context()
        task_id = make_uuid()
        celery.send_task(
            'vectorstorer.delete',
            args=[resource, context, backend_context],
            task_id=task_id)

def _get_resource_list_for_deletion(
        resource_dict,
        package_resources,
        parent_resource):
    '''Returns a list with the resources that have to be deleted'''

    resources_to_delete = []
    if resource_dict['format'] == DBTableResource.FORMAT:
        resources_to_delete = _get_child_resources(resource_dict)
    else:
        parent_child_resources = []
        if parent_resource is not None:
            #find the parent resource of the deleted one
            for child_res in package_resources:
                if ('parent_resource_id' in child_res and
                        child_res['parent_resource_id'] == resource_dict[
                            'parent_resource_id'] and
                        child_res['state'] == 'active'):
                    parent_child_resources.append(child_res)
        if len(parent_child_resources) < 1:
            resources_to_delete.append(parent_resource)
    return resources_to_delete

def _get_parent_resource(resource_dict, package_resources):
    '''Searches in package resources to find the parent
    resource of the requested one. If not found retuns None'''
    parent_id = resource_dict.get('parent_resource_id')
    if not parent_id:
        return None
    parent_resource = None
    for r in package_resources:
        if (r['id'] == parent_id and r['state'] == 'active'):
            parent_resource = r
            break
    return parent_resource

def _get_child_resources(parent_resource):
    '''Returns the child resources of the parent resource'''
    
    # Get the resource again as an Object and then dict
    # because the dict returned from the api doesn't contain
    # the package id
    par_resource_obj = model.Session.query(model.Resource).get(
        parent_resource['id'])
    parent_resource = par_resource_obj.as_dict()
    
    user = _get_site_user()
    action_context = {'model': model, 'user': user.get('name')}
    current_package = toolkit.get_action('package_show')(
        action_context, {'id': parent_resource['package_id']})
    package_resources = current_package['resources']
    
    child_resources = []
    for child_resource in package_resources:
        if 'parent_resource_id' in child_resource:
            if child_resource['parent_resource_id'] == parent_resource['id'] and child_resource['state']=='active':
                child_resources.append(child_resource)
    return child_resources
