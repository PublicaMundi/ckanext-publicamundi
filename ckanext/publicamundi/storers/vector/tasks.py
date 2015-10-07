import os
import copy
import urllib2
import urllib
import json
import shutil
import magic
from urlparse import urlparse
from pyunpack import Archive

import celery
from celery.task.http import HttpDispatchTask

from ckan.lib.celery_app import celery as celery_app

import ckanext.publicamundi.storers.vector as vectorstorer
from ckanext.publicamundi.storers.vector import vector
from ckanext.publicamundi.storers.vector.resources import(
    WMSResource, DBTableResource, WFSResource)
from ckanext.publicamundi.storers.vector.db_helpers import DB
from ckanext.publicamundi.storers.vector.lib import utils

# List MIME types recognized as archives from pyunpack
archive_mime_types = [
    'application/zip',
    'application/gzip',
    'application/x-7z-compressed',
    'application/x-tar',
    'application/x-rar',
]

class CannotDownload(RuntimeError):
    pass

class CannotPublishLayer(RuntimeError):
    pass

def setup_vectorstorer_in_task_context(context):
    '''The vectorstorer module needs to be setup before any task actually
    does anything. 
    
    This is because we need to configure the module based on the setting 
    supplied in our central *.ini configuration. 
    '''

    temp_folder = context['temp_folder']
    gdal_folder = context['gdal_folder']
    vectorstorer.setup(gdal_folder, temp_folder)
    return

@celery_app.task(name='vectorstorer.identify', max_retries=2)
def identify_resource(resource_dict, context):
    setup_vectorstorer_in_task_context(context)
    
    logger = identify_resource.get_logger()
    
    api_key = context['user_api_key']
    resource_id = resource_dict['id']
    
    # Download

    try:
        tmp_folder, filename = _download_resource(resource_dict, api_key)
    except CannotDownload as ex:
        # Retry later, maybe the resource is still uploading
        logger.error('Failed to identify: %s' % (ex.message))
        identify_resource.retry(exc=ex, countdown=60)
    logger.info('Downloaded resource %s at %s' % (resource_id, tmp_folder))

    # Identify downloaded resource

    result = None
    try:
        result = _identify_resource(resource_dict, api_key, tmp_folder, filename)
        logger.info('Identified resource %s' % (resource_id))
    except vector.DatasourceException as ex:
        logger.error('Failed to identify resource %s: %s' % (resource_id, ex))
        raise 
    finally:
        _delete_temp(tmp_folder)

    return result

def _identify_resource(resource, user_api_key, resource_tmp_folder, filename):
    
    # Todo: Document this function

    result = {}

    gdal_driver, vector_file_path, prj_exists = _get_gdalDRV_filepath(
        resource, resource_tmp_folder, filename)

    if gdal_driver:
        result['gdal_driver'] = gdal_driver
        _vector = vector.Vector(gdal_driver, vector_file_path, None, None)
        layer_count = _vector.get_layer_count()
        layers = []
        for layer_idx in range(0, layer_count):
            layer_dict = {}
            layer = _vector.get_layer(layer_idx)
            layer_dict['idx'] = layer_idx
            layer_dict['layer_name'] = layer.GetName()
            layer_dict['layer_srs'] = _vector.get_SRS(layer)
            layer_dict['layer_geometry'] = _vector.get_geometry_name(layer)
            sample_data = _vector.get_sample_data(layer)
            layer_dict['sample_data'] = sample_data
            layers.append(layer_dict)

        result['layers'] = layers

    return result

@celery_app.task(name='vectorstorer.upload')
def vectorstorer_upload(resource_dict, context, backend_context):
    setup_vectorstorer_in_task_context(context)
   
    db_conn_params = context['db_params']
    api_key = context['user_api_key']
    resource_id = resource_dict['id']
    
    logger = vectorstorer_upload.get_logger()
    
    # Download

    tmp_folder, filename = _download_resource(resource_dict, api_key)
    logger.info(
        'Downloaded resource %s at %s' % (resource_id, tmp_folder))
    
    # Prepare a context object for ingestion
    # Note: Dont clutter task's context with non-seriazable objects

    context1 = copy.deepcopy(context)
    context1['logger'] = logger

    # Ingest
    
    try:
        _ingest_resource(
            resource_dict,
            context1,
            backend_context,
            tmp_folder,
            filename)
        logger.info('Ingested resource %s' % (resource_id))
    except Exception as ex:
        logger.error(
            'Failed to ingest resource %s: %s' % (resource_id, ex))
        raise
    finally:
        _delete_temp(tmp_folder)

    # Reload configuration at backend 
    
    try:
        _reload_geoserver_config(context1, backend_context['geoserver_context'])
    except Exception as ex:
        logger.warning('Failed to reload backend configuration: %s' % (ex))

    return

def _ingest_resource(
        resource,
        context,
        backend_context,
        resource_tmp_folder,
        filename):
    
    # Todo: 
    #  a. Document this function
    #  b. This is a core processing unit and should return an overall status

    gdal_driver, vector_file_path, prj_exists = _get_gdalDRV_filepath(
        resource, resource_tmp_folder, filename)

    db_conn_params = context['db_params']
    layer_params = context['layer_params']['layers']
    
    logger = context['logger']

    if gdal_driver:
        
        if gdal_driver == vector.SHAPEFILE:
            _encoding = layer_params[0]['encoding']
        else:
            _encoding = 'utf-8'

        logger.info('Using encoding `%s` for input file', _encoding)
        
        _vector = vector.Vector(
            gdal_driver,
            vector_file_path,
            _encoding,
            db_conn_params)
        logger.info('Read vector resource using GDAL');

        layer_count = _vector.get_layer_count()
        logger.info('Found %d vector layers to ingest' % (layer_count))

        for layer_idx in range(0, layer_count):
            if layer_params[layer_idx]['is_selected']:
                layer_name = layer_params[layer_idx]['name']
                srs = layer_params[layer_idx]['srs']
                encoding = layer_params[layer_idx]['encoding']
                logger.info('Trying to ingest selected vector layer `%s` (at epsg:%s)', layer_name, srs)
                _ingest_vector(
                    _vector,
                    layer_idx,
                    layer_name,
                    resource,
                    context,
                    backend_context,
                    srs,
                    encoding)

def _get_gdalDRV_filepath(resource, resource_tmp_folder, file_name):
    '''Tries to find the vector file which is going to be read by GDAL.
    
    Returns the gdal driver name, the vector file path and if the vector
    file is a Shapefile , the existence if the .prj file.

    param resource_tmp_folder: The path of the created folder containing
    the resource as it was downloaded
    '''
    
    global archive_mime_types

    actual_resource_parent_folder = resource_tmp_folder
    downloaded_res_file = os.path.join(resource_tmp_folder, file_name)

    mimetype = magic.from_file(downloaded_res_file, mime=True)

    # If the mimetype of the resource is an Archive format, extract the files
    # and set the extaction folder as the folder to search for the vector file

    if mimetype in archive_mime_types:
        base = os.path.basename(downloaded_res_file)
        file_name_wo_ext = os.path.splitext(base)[0]
        extraction_folder = os.path.join(resource_tmp_folder, file_name_wo_ext)
        os.makedirs(extraction_folder)
        Archive(downloaded_res_file).extractall(extraction_folder)
        file_extracted_folder = _get_file_folder(extraction_folder)
        actual_resource_parent_folder = file_extracted_folder

    gdal_driver, vector_file_name, prj_exists = _get_file_path(
        actual_resource_parent_folder, resource)
    vector_file_path = os.path.join(
        actual_resource_parent_folder,
        vector_file_name)

    return gdal_driver, vector_file_path, prj_exists

def _get_file_folder(extraction_folder):
    files_folder = None
    for dirName, subdirList, fileList in os.walk(extraction_folder):
        if len(fileList) > 0:
            files_folder = dirName
            break
    return files_folder

def _download_resource(resource_dict, api_key):
    '''Downloads the HTTP resource specified in resource-url and saves it inder a 
    temporary folder.
    '''

    temp_folder = os.path.join(vectorstorer.temp_dir, resource_dict['id'])
    os.makedirs(temp_folder)
    
    resource_url = urllib2.unquote(resource_dict['url'])
    is_upload = resource_dict.get('url_type', '') == 'upload'

    # Prepare download request

    download_request = urllib2.Request(resource_url)
    if is_upload:
        download_request.add_header('Authorization', api_key)
    
    # Perform request, handle errors
    
    try:
        download_response = urllib2.urlopen(download_request)
    except urllib2.HTTPError as ex:
        _delete_temp(temp_folder)
        try:
            detail = ex.read(128)
        except:
            detail = 'n/a'
        raise CannotDownload(
            'Failed to download %s: %s: %s' % (resource_url, ex, detail))
    except urllib2.URLError as ex:
        _delete_temp(temp_folder)
        raise CannotDownload(
            'Failed to download %s: %s' % (resource_url, ex))

    # Save downloaded resource in a local file
    
    filename = urlparse(resource_url).path.split('/')[-1]
    downloaded_file = os.path.join(temp_folder, filename)
    with open(downloaded_file, 'wb') as ofp:
        ofp.write(download_response.read())
        ofp.close()

    return temp_folder, filename

def _reload_geoserver_config(context, geoserver_context):
    
    reload_url = geoserver_context.get('reload_url', '')
    if reload_url.startswith('http://'):
        # Fire this task in a synchronous manner
        r = HttpDispatchTask.delay(url=reload_url, method='GET')
        r.get(timeout=30)
    
    return

def _get_file_path(resource_tmp_folder, resource):
    '''Looking into the downladed or extracted folder for the resource
    based on the resource format.

    Returns the actual vector file name , the gdal driver name and the
    existence of the .prj file if the resource format is shapefile'''

    vector_file = None
    gdal_driver = None
    prj_exists = False

    resource_format = resource['format'].lower()
    file_list = os.listdir(resource_tmp_folder)

    if resource_format == "shapefile":
        is_shp, vector_file, prj_exists = _is_shapefile(resource_tmp_folder)
        if is_shp:
            gdal_driver = vector.SHAPEFILE
    elif resource_format == 'kml':
        vector_file = get_file_by_extention(file_list, '.kml')
        gdal_driver = vector.KML
    elif resource_format == 'gml':
        vector_file = get_file_by_extention(file_list, '.gml')
        gdal_driver = vector.GML
    elif resource_format == 'gpx':
        vector_file = get_file_by_extention(file_list, '.gpx')
        gdal_driver = vector.GPX
    elif resource_format == 'geojson':
        vector_file = get_file_by_extention(file_list, '.geojson')
        gdal_driver = vector.GEOJSON
    elif resource_format == 'json':
        vector_file = get_file_by_extention(file_list, '.json')
        gdal_driver = vector.GEOJSON
    elif resource_format == 'sqlite':
        vector_file = get_file_by_extention(file_list, '.sqlite')
        gdal_driver = vector.SQLITE
    elif resource_format == 'geopackage':
        vector_file = get_file_by_extention(file_list, '.geopackage')
        gdal_driver = vector.GEOPACKAGE
    elif resource_format == 'gpkg':
        vector_file = get_file_by_extention(file_list, '.gpkg')
        gdal_driver = vector.GEOPACKAGE
    elif resource_format == 'csv':
        vector_file = get_file_by_extention(file_list, '.csv')
        gdal_driver = vector.CSV
    elif resource_format == 'xls':
        vector_file = get_file_by_extention(file_list, '.xls')
        gdal_driver = vector.XLS
    elif resource_format == 'xlsx':
        vector_file = get_file_by_extention(file_list, '.xlsx')
        gdal_driver = vector.XLS
    if vector_file is None:
        raise vector.DatasourceException
    return gdal_driver, vector_file, prj_exists

def get_file_by_extention(file_list, extention):
    '''Looking into the download or extracted folder for the file
    based on the resource format which was was entered from the user
    '''
    
    file_name = None
    for _file in file_list:
        if _file.lower().endswith(extention):
            file_name = _file
    return file_name

def _make_tmp_file_name(resource):
    resource_url = urllib2.unquote(resource['url']).decode('utf8')
    url_parts = resource_url.split('/')
    resource_file_name = url_parts[len(url_parts) - 1]
    return resource_file_name

def _ingest_vector(
        _vector,
        layer_idx,
        layer_name,
        resource,
        context,
        backend_context,
        srs,
        encoding):
    
    # Todo: 
    #  a. Document this function
    #  b. Emit errors/warnings for the several parts that can fail
   
    logger = context['logger']

    layer = _vector.get_layer(layer_idx)

    srs = int(srs)
    if layer and layer.GetFeatureCount() > 0:
        #layer_name = layer.GetName()
        geom_name = _vector.get_geometry_name(layer)
        spatial_ref = vectorstorer.osr.SpatialReference()
        spatial_ref.ImportFromEPSG(srs)
        
        created_db_table_resource = _add_db_table_resource(
            context,
            resource,
            geom_name,
            layer_name)
        layer = _vector.get_layer(layer_idx)

        _vector.handle_layer(
            layer,
            geom_name,
            created_db_table_resource['id'].lower(),
            srs,
            encoding)

        publishing_server = backend_context['default_publishing_server']
        publishing_server_url = None
        publishing_layer = None
        
        logger.info('About to publish %s layer `%s` (originally named as `%s`) at %s backend', 
            geom_name, layer_name, layer.GetName(), publishing_server)

        # Publish to Geoserver or Mapserver (Based on configuration)
        if publishing_server == 'geoserver':
            publishing_server_url, publishing_layer = _publish_layer_to_geoserver(
                backend_context['geoserver_context'], layer_name,
                created_db_table_resource, spatial_ref)
        elif publishing_server == 'mapserver':
            publishing_server_url, publishing_layer = _publish_layer_to_mapserver(
                context, backend_context['mapserver_context'], layer_name,
                created_db_table_resource,spatial_ref, srs, layer, geom_name)
            mapping_server = "mapserver"

        logger.info('Published layer `%s` under %s backend: %s' % (
            publishing_layer, publishing_server, publishing_server_url))

        _add_wms_resource(
            context,
            layer_name,
            resource,
            created_db_table_resource,
            publishing_server_url,
            publishing_layer)

        _add_wfs_resource(
            context,
            layer_name,
            resource,
            created_db_table_resource,
            publishing_server_url,
            publishing_layer)

def _add_db_table_resource(context, resource, geom_name, layer_name):
    db_table_resource = DBTableResource(
        context['package_id'],
        layer_name,
        'A PostGis table generated from `%s`' % (resource['name']),
        resource['id'],
        resource['url'],
        geom_name)
    created_db_table_resource = _invoke_api_resource_action(
        context, db_table_resource.as_dict(), 'resource_create')
    return created_db_table_resource

def _add_wms_resource(
        context,
        layer_name,
        resource,
        parent_resource,
        wms_server,
        wms_layer):
    wms_resource = WMSResource(
        context['package_id'],
        layer_name,
        'A WMS layer generated from `%s`' % (resource['name']),
        parent_resource['id'],
        wms_server,
        wms_layer)
    created_wms_resource = _invoke_api_resource_action(
        context, wms_resource.as_dict(), 'resource_create')
    return created_wms_resource

def _add_wfs_resource(
        context,
        layer_name,
        resource,
        parent_resource,
        wfs_server,
        wfs_layer):
    wfs_resource = WFSResource(
        context['package_id'],
        layer_name,
        'A WFS layer generated from `%s`' % (resource['name']),
        parent_resource['id'],
        wfs_server,
        wfs_layer)
    created_wfs_resource = _invoke_api_resource_action(
        context, wfs_resource.as_dict(), 'resource_create')
    return created_wfs_resource

def _delete_temp(res_tmp_folder):
    shutil.rmtree(res_tmp_folder)

def _is_shapefile(res_folder_path):
    shp_exists = False
    shx_exists = False
    dbf_exists = False
    prj_exists = False
    for _file in os.listdir(res_folder_path):
        if _file.lower().endswith('.shp'):
            shapefile_name = _file
            shp_exists = True
        elif _file.lower().endswith('.shx'):
            shx_exists = True
        elif _file.lower().endswith('.dbf'):
            dbf_exists = True

    if shp_exists and shx_exists and dbf_exists:
        return (True, shapefile_name, prj_exists)
    else:
        return (False, None, False)

def _publish_layer_to_geoserver(geoserver_context, layer_name, resource, spatial_ref):
    '''Publish an existing PostGis layer (previously ingested as a table resource) 
    to our Geoserver backend.
    '''

    srs_wkt = spatial_ref.ExportToWkt()

    api_url = geoserver_context['api_url']
    public_url = geoserver_context['url']
    workspace = geoserver_context['workspace']
    username = geoserver_context['username']
    password = geoserver_context['password']
    datastore = geoserver_context['datastore']

    req_body = u'''
    <featureType>
        <name>%s</name>
        <title>%s</title>
        <abstract>%s</abstract>
        <nativeCRS>%s</nativeCRS>
    </featureType>
    ''' % (resource['id'], layer_name, resource['description'], srs_wkt)

    req = urllib2.Request(
        api_url + '/rest' + 
        '/workspaces/' + workspace + 
        '/datastores/' + datastore + 
        '/featuretypes')
    req.add_header('Content-Type', 'text/xml')
    req.add_data(req_body.encode('utf-8'))
    req.add_header('Authorization', 'Basic ' + (
        (username + ':' + password).encode('base64').rstrip()))

    try:
        res = urllib2.urlopen(req)
    except urllib2.HTTPError as ex:
        try:
            detail = ex.read()
        except:
            detail = 'n/a'
        raise CannotPublishLayer(
            'Failed to publish layer %r: %s: %s' % (layer_name, ex, detail))

    layer_name = workspace + ':' + resource['id']
    return (public_url, layer_name)

def _publish_layer_to_mapserver(
        context,
        mapserver_context,
        layer_name,
        resource,
        spatial_ref,
        srs,
        layer,
        geom_name):

    from ckanext.publicamundi.storers.vector import mapserver_utils

    srs_wkt = spatial_ref.ExportToWkt()
    package_id = context['package_id']
    package = {'id': package_id}
    pkg_dict = _invoke_api_resource_action(
                    context,
                    package,
                    'package_show')
    pkg_name = pkg_dict['name']
    mapfile_name = pkg_name + '.map'

    mapfile_folder = mapserver_context['mapfile_folder']
    if not os.path.exists(mapfile_folder):
        os.makedirs(mapfile_folder)
    abs_mapfile = os.path.join(mapfile_folder, mapfile_name)
    
    mapsrv_params = 'map='+ abs_mapfile
    
    mapserver_url =mapserver_context['url']+ "?" + mapsrv_params

    _mapserverutils = mapserver_utils.MapServerUtils(vectorstorer)
    map = None

    if os.path.exists(abs_mapfile):
        map = _mapserverutils.load_mapfile(abs_mapfile)
    else:
        map =_mapserverutils.create_mapfile_obj(
                mapfile_folder,
                mapserver_url,
                pkg_name)

    new_layer = _mapserverutils.create_layer(
                    map,
                    resource['id'],
                    layer,
                    layer_name,
                    geom_name,
                    srs,
                    srs_wkt,
                    context['db_params'])

    map.insertLayer(new_layer)
    mapserver_layer_name = new_layer.name
    minx, miny, maxx, maxy = _mapserverutils._calc_mapfile_extent(map)

    map = _mapserverutils.update_srs_list(map, srs)

    r_obj = _mapserverutils.create_mapscript_rect_obj(minx, miny, maxx, maxy)
    map.extent = r_obj

    map.setExtent(r_obj.minx, r_obj.miny, r_obj.maxx, r_obj.maxy)

    map.save(abs_mapfile)

    return mapserver_url, mapserver_layer_name

def _invoke_api_resource_action(context, resource, action):
    api_key = context['user_api_key']
    site_url = context['site_url']
    data_string = urllib.quote(json.dumps(resource))
    request = urllib2.Request(site_url + 'api/action/' + action)
    request.add_header('Authorization', api_key)
    response = urllib2.urlopen(request, data_string)
    created_resource = json.loads(response.read())['result']
    return created_resource

def _update_resource_metadata(context, resource):
    api_key = context['user_api_key']
    site_url = context['site_url']
    resource['vectorstorer_resource'] = True
    data_string = urllib.quote(json.dumps(resource))
    request = urllib2.Request(site_url + 'api/action/resource_update')
    request.add_header('Authorization', api_key)
    urllib2.urlopen(request, data_string)

@celery_app.task(name='vectorstorer.update')
def vectorstorer_update(resource_dict, context, backend_context): 
    setup_vectorstorer_in_task_context(context)

    db_conn_params = context['db_params']
    resource_ids = context['resource_list_to_delete']

    logger = vectorstorer_update.get_logger()
    context['logger'] = logger

    if len(resource_ids) > 0:
        for res_id in resource_ids:
            res = {'id': res_id}
            try:
                _invoke_api_resource_action(context, res, 'resource_delete')
            except urllib2.HTTPError as e:
                # Fixme proper logging
                print e.reason

    # Fixme: Wrap in an try block as inside vectorstorer.upload
    _ingest_resource(resource_dict, context, backend_context)

@celery_app.task(name='vectorstorer.delete')
def vectorstorer_delete(resource_dict, context, backend_context): 
    setup_vectorstorer_in_task_context(context)

    db_conn_params = context['db_params']

    logger = vectorstorer_delete.get_logger()
    context['logger'] = logger

    resources_to_delete = context['resource_list_to_delete']   
    publishing_server = backend_context['default_publishing_server']

    # If resource dict is None a parent vector resource
    # has been deleted. So we skip the next checks
    if resource_dict is not None:
        # A vector child resource has been deleted
        if 'format' in resource_dict:
            if resource_dict['format'] == DBTableResource.FORMAT:
                # A DBTable resource was deleted, so delete the table
                # from the database
                _delete_from_datastore(
                    resource_dict['id'],
                    db_conn_params,
                    context,
                    logger)
            elif resource_dict['format'] in [
                WMSResource.FORMAT, WFSResource.FORMAT]:
                # A WMS or WFS resource was deleted, so unpublish it from backend
                if publishing_server == 'geoserver':
                    _unpublish_from_geoserver(
                        resource_dict,
                        backend_context['geoserver_context'],
                        logger)
                elif publishing_server == 'mapserver':
                    _unpublish_from_mapserver(
                        resource_dict,
                        context,
                        backend_context['mapserver_context'],
                        logger)
    
    # Delete the resources that are in the list. For example
    # if a DB_Table resouce was deleted, this list contains
    # the WMS and WFS resource.
    for resource in resources_to_delete:
        if resource is not None:
            if resource['format'] == DBTableResource.FORMAT:
                # A DBTable resource was deleted, so delete the table
                # from the database
                _delete_from_datastore(
                    resource['id'],
                    db_conn_params,
                    context,
                    logger)
            elif resource['format'] in [
                WMSResource.FORMAT, WFSResource.FORMAT]:
                # A WMS or WFS resource will be deleted, so unpublish it
                # from backend
                if publishing_server == 'geoserver':
                    _unpublish_from_geoserver(
                        resource,
                        backend_context['geoserver_context'],
                        logger)
                elif publishing_server == 'mapserver':
                    _unpublish_from_mapserver(
                        resource,
                        context,
                        backend_context['mapserver_context'],
                        logger)

    # After doing unpublish and delete operations for child resources
    # delete the from ckan
    for resource in resources_to_delete:
        res = {'id': resource['id']}
        try:
            _invoke_api_resource_action(context, res, 'resource_delete')
        except urllib2.HTTPError as e:
            print e.reason

def _delete_from_datastore(resource_id, db_conn_params, context, logger):
    from psycopg2 import ProgrammingError
    try:
        _db = DB(db_conn_params)
        _db.drop_table(resource_id)
        _db.commit_and_close()
        logger.info('Deleted table %s from the Database'
            % (resource_id))
    except ProgrammingError as ex:
        logger.error('Failed to delete table %s from the database: %s'
            % (resource_id, ex))

def _unpublish_from_geoserver(resource, geoserver_context, logger):
    '''Contact Geoserver and unpublish a layer previously created as an 
    ingested resource.
    '''

    from geoserver.catalog import Catalog, FailedRequestError
    
    layer_name = None
    if resource['format'] == WMSResource.FORMAT:
        layer_name = resource['wms_layer']
    else:
        layer_name = resource['wfs_layer']
    
    try:
        api_url = geoserver_context['api_url']
        cat = Catalog(
            api_url + '/rest',
            username=geoserver_context['username'],
            password=geoserver_context['password'])
        layer = cat.get_layer(resource['parent_resource_id'].lower())
        cat.delete(layer)
        cat.reload()
        logger.info('Unpublished layer %s from Geoserver'
            % (layer_name))
    except AttributeError as ex:
        logger.error('Failed to unpublish layer %s: %s' % (layer_name, ex))
    except FailedRequestError as ex:
         logger.error('Failed to unpublish layer %s: %s' % (layer_name, ex))

def _unpublish_from_mapserver(resource, context, mapserver_context, logger):
    
    from ckanext.publicamundi.storers.vector import mapserver_utils
    
    layer_name = None
    if resource['format'] == WMSResource.FORMAT:
        layer_name = resource['wms_layer']
    else:
        layer_name = resource['wfs_layer']

    package_id = context['package_id']
    package = {'id': package_id}
    pkg_dict = _invoke_api_resource_action(
                    context,
                    package,
                    'package_show')
    pkg_name = pkg_dict['name']
    mapfile_name = pkg_name + '.map'

    mapfile_folder = mapserver_context['mapfile_folder']

    abs_mapfile = os.path.join(mapfile_folder, mapfile_name)

    _mapserverutils = mapserver_utils.MapServerUtils(vectorstorer)

    try:
        map = _mapserverutils.load_mapfile(abs_mapfile)
        _mapserverutils.delete_layer(map, layer_name)
        map.save(abs_mapfile)

    except Exception as ex:
        logger.error('Failed to unpublish layer %s: %s'
            % (layer_name, ex))

