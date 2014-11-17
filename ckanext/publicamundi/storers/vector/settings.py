from pylons import config

import sys
sys.path.append(config.get('ckanext-vectorstorer.gdal_folder', '/usr/lib/python2.7/dist-packages'))

from osgeo import gdal
	    
	    
from osgeo import ogr, osr

osr.UseExceptions()
ogr.UseExceptions()

db_encoding='utf-8'
TMP_FOLDER='/tmp/vectorstorer/'

VECTOR_FORMATS= [ 
    'shapefile',
    'kml',
    'gml',
    #'gpx',
    'csv',
    'geojson',
    'sqlite',
    'geopackage',
    'gpkg']

 

ARCHIVE_MIMETYPES = [
    'application/zip',
    'application/gzip',
    'application/x-7z-compressed',
    'application/x-tar',
    'application/x-rar',
     ]
 


WMS_VECTORSTORER_RESOURCE=u'vectorstorer_wms'
DB_TABLE_RESOURCE=u'vectorstorer_db'
WMS_FORMAT=u'wms'
DB_TABLE_FORMAT=u'data_table'