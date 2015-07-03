from pylons import config

PUBLISHED_AT_GEOSERVER = "geoserver"
PUBLISHED_AT_MAPSERVER = "mapserver"

def get_publishing_server(resource):
    ''' Compares a WMS resource URL to mapping server
    urls found in config file. Returns mapserver or
    geoserver.'''
    
    geoserver_url = None
    mapserver_url = None
    try:
        geoserver_url = config['ckanext.publicamundi.vectorstorer.geoserver.url']
    except KeyError:
        pass
    
    try:
        mapserver_url = config['ckanext.publicamundi.vectorstorer.mapserver.url']
    except KeyError:
        pass
    
    if geoserver_url in resource['wms_server']:
        return PUBLISHED_AT_GEOSERVER
    elif mapserver_url in resource['wms_server']:
        return PUBLISHED_AT_MAPSERVER