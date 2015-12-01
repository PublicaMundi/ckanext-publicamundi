import logging
import json
from raster_plugin_util import RasterUtil, CannotDownload
from ckan.lib.celery_app import celery as celery_app
import ckanext.publicamundi.storers.raster as rasterstorer




@celery_app.task(name='rasterstorer.identify', max_retries=3)
def rasterstorer_identify(context):
    """
    Task for downloading the resource and preparing it for ingest
    @:param context: the context in which to execute the task
    """
    log = rasterstorer_identify.get_logger()

    log.info('Received an identify task: context=\n%s' % (json.dumps(context, indent=4)))

    try:
        log.info("[Raster_Identify]Downloading resource %s..." % context["resource_dict"]["id"])
        util = RasterUtil(context, log)
        util.download_resource()
        log.info('[Raster_Identify]Downloaded resource %s' % context["resource_dict"]["id"])
    except CannotDownload as ex:
        # Retry later, maybe the resource is still uploading
        log.error('[Raster_Identify] Failed to download: %s' % ex.message)
        rasterstorer_identify.retry(exc=ex, countdown=60)


@celery_app.task(name='rasterstorer.import')
def rasterstorer_import(context):
    """
    Task for publishing a raster in celery app. Keep it simple, initialize the context correctly then generate a gml
    and submit it to petascope
    @:param context the context in which to execute the task
    """
    log = rasterstorer_import.get_logger()
    try:
        setup_rasterstorer_in_task_context(context)
        util = RasterUtil(context, log)
        util.insert_coverage()
        util.check_import_successful()
        util.add_wcs_resource()
        util.add_wms_resource()
        util.finalize()
        log.info("[Raster_Import]Resource %s was imported successfully." % (context["resource_dict"]["id"]))
    except Exception as ex:
        log.info("[Raster_Import]Resource %s could not be imported. Exception message: %s"
                 % (context["resource_dict"]["id"], ex.message))
        raise


@celery_app.task(name='rasterstorer.delete')
def rasterstorer_delete(context):
    """
    Task for deleting a raster in celery app. Keep it simple, we just need to call WCST DeleteCoverage request and
    it will take care of the rest
    @:param resource_id the id of the resource to be imported
    @:param context the context in which to execute the task
    """
    log = rasterstorer_delete.get_logger()
    try:
        log.info("[Raster_Delete]Deleting resource %s..." % context["resource_dict"]["id"])
        util = RasterUtil(context, log)
        util.delete_coverage()
        log.info("[Raster_Delete]Resource %s was deleted successfully." % (context["resource_dict"]["id"]))
    except Exception as ex:
        log.info("[Raster_Delete]Resource %s could not be deleted. Exception message %s"
                 % (context["resource_dict"]["id"], ex.message))
        raise


def setup_rasterstorer_in_task_context(context):
    """
    The vectorstorer module needs to be setup before any task actually
    does anything.

    This is because we need to configure the module based on the setting
    supplied in our central *.ini configuration.
    :param context: the context of the task
    """

    temp_folder = context['temp_folder']
    gdal_folder = context['gdal_folder']
    rasterstorer.setup(gdal_folder, temp_folder)
    return
