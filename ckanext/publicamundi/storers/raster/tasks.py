import urllib as url_lib
import logging

from ckan.lib.celery_app import celery as celery_app


log = logging.getLogger(__name__)

@celery_app.task(name='rasterstorer.import')
def rasterstorer_import(resource_id, context):
    """
    Task for publishing a raster in celery app. Keep it simple, we just need to call /api/raster/publish/{dataset_id} and
    it will take care of the rest
    @:param resource_id the id of the resource to be imported
    @:param context the context in which to execute the task
    """
    try:
        service_call = context['service_call']
        response = url_lib.urlopen(service_call).read()
        log.info("Resource %s was imported successfully." % resource_id)
    except IOError as ex:
        log.info("Resource %s could not be imported." % resource_id)
        raise


@celery_app.task(name='rasterstorer.delete')
def rasterstorer_delete(resource_id, context):
    """
    Task for deleting a raster in celery app. Keep it simple, we just need to call /api/raster/delete/{dataset_id} and
    it will take care of the rest
    @:param resource_id the id of the resource to be imported
    @:param context the context in which to execute the task
    """
    try:
        service_call = context['service_call']
        response = url_lib.urlopen(service_call).read()
        log.info("Resource %s was deleted successfully." % resource_id)
    except IOError as ex:
        log.info("Resource %s could not be deleted." % resource_id)
        raise


