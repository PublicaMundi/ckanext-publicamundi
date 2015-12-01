from pylons import config

from ckan.model.types import make_uuid
from ckan.lib.celery_app import celery
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.lib.dictization.model_dictize import resource_dictize
from ckanext.publicamundi.model.resource_ingest import (
    ResourceIngest, ResourceStorerType, IngestStatus)


def _get_site_url():
    """
    Returns the url of the ckan website
    :return: the url of the ckan website
    """
    try:
        return h.url_for_static('/', qualified=True)
    except AttributeError:
        return config.get('ckan.site_url', '')


def _get_site_user():
    """
    Returns the current logged user
    :return: the current logged in user
    """
    user = toolkit.get_action('get_site_user')({
        'model': model,
        'ignore_auth': True,
        'defer_commit': True
    }, {})
    return user


def _make_default_context():
    """
    The default context for celery tasks. For the raster storer
    we only need the site url, the user name and api key and the path to the temp dir
    :return: the default context
    """
    user = _get_site_user()
    return {
        'site_url': _get_site_url(),
        # User on behalf of which a task is executed
        'user_name': user['name'],
        'user_api_key': user['apikey'],
        # Configuration needed to setup raster storer
        'temp_folder': config.get('ckanext.publicamundi.rasterstorer.temp_dir', ""),
        'wms_base_url': config.get("ckanext.publicamundi.rasterstorer.wms_base_url", ""),
        'wcst_import_url': config.get("ckanext.publicamundi.rasterstorer.wcst_import_url", ""),
        'wcst_base_url': config.get("ckanext.publicamundi.rasterstorer.wcst_base_url", ""),
        'gdal_folder': config.get("ckanext.publicamundi.rasterstorer.gdal_folder", "")
        }


def create_identify_resource_task(resource):
    """
    Creates the celery task to identify the resource
    :param resource: the resource to be identified
    """

    task_id = make_uuid()
    
    # We are using resource_dictize() just to force CKAN to provide an absolute url
    # Note Maybe a more clean way to achive this would be to call something like 
    # url_for(controller='package', action='resource_download', id=package_id, resource_id=resource_id)
    package_id = resource.as_dict()['package_id']
    resource_dict = resource_dictize(resource, {'model': model})
    resource_dict['package_id'] = package_id
    
    context = _make_default_context()
    context['resource_dict'] = resource_dict
    celery.send_task(
        'rasterstorer.identify',
        args=[context],
        task_id=task_id
    )

    res_identify = model.Session.query(ResourceIngest).filter(
        ResourceIngest.resource_id == resource.id).first()
    if res_identify:
        # This is when a user had previously rejected the ingestion workflow,
        # but now wants to re-identify the resource
        model.Session.delete(res_identify)
        new_res_identify = ResourceIngest(
            task_id,
            resource.id,
            ResourceStorerType.RASTER
        )
        model.Session.add(new_res_identify)
        model.Session.commit()
    else:
        # A newly created/updated resource needs to be identified
        new_res_identify = ResourceIngest(
            task_id,
            resource.id,
            ResourceStorerType.RASTER
        )
        model.Session.add(new_res_identify)


def create_ingest_resource_task(resource):
    """
    Creates the celery task for raster resource ingestion
    :param resource: the resource to be ingested
    """
    task_id = make_uuid()
    context = _make_default_context()
    resource_dict = resource.as_dict()
    context['resource_dict'] = resource_dict
    celery.send_task(
        'rasterstorer.import',
        args=[context],
        task_id=task_id
    )


def create_delete_resource_task(resource):
    """
    Creates the celery task for raster resource deletion
    :param resource: the resource to be deleted
    """
    context = _make_default_context()
    context['resource_dict'] = resource
    task_id = make_uuid()
    celery.send_task(
        'rasterstorer.delete',
        args=[context],
        task_id=task_id
    )


def change_resource_to_published(resource):
    """
    Marks the resource as published
    :param resource: the resource to be marked
    """
    res_ingest = model.Session.query(ResourceIngest).filter(
        ResourceIngest.resource_id == resource.id).first()
    res_ingest.status = IngestStatus.PUBLISHED
    model.Session.commit()
