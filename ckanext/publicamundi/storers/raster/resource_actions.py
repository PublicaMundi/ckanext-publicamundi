from pylons import config

from ckan.model.types import make_uuid
from ckan.lib.celery_app import celery
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as toolkit
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
        'temp_folder': config.get(
            'ckanext.publicamundi.rasterstorer.temp_dir'),
        }



def create_ingest_resource_task(resource):
    """
    Creates the celery task for raster resource ingestion
    :param resource: the the resource to be ingested
    """
    task_id = make_uuid()
    context = {
        'service_call': _get_site_url() + "api/raster/publish/" + resource.id
    }
    celery.send_task(
        'rasterstorer.import',
        args=[resource.id, context],
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
            ResourceStorerType.RASTER,
            IngestStatus.PUBLISHED)
        model.Session.add(new_res_identify)
        model.Session.commit()
    else:
        # A newly created/updated resource needs to be identified
        new_res_identify = ResourceIngest(
            task_id,
            resource.id,
            ResourceStorerType.RASTER,
            IngestStatus.PUBLISHED)
        model.Session.add(new_res_identify)


def create_delete_resource_task(resource_id):
    """
    Creates the celery task for raster resource deletion
    :param resource_id: the id of the resource to be deleted
    """
    context = {
        'service_call': _get_site_url() + "api/raster/delete/" + resource_id
    }
    task_id = make_uuid()
    celery.send_task(
        'rasterstorer.delete',
        args=[resource_id, context],
        task_id=task_id
    )