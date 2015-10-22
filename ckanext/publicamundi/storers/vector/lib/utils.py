from pylons import config

PUBLISHED_AT_GEOSERVER = "geoserver"
PUBLISHED_AT_MAPSERVER = "mapserver"

def get_publishing_server(resource, backend_context=None):
    ''' Compares a WMS resource URL to mapping server
    urls found in config file. Returns mapserver or
    geoserver.'''

    geoserver_url = None
    mapserver_url = None
    
    if not backend_context:
        # used by ckan instance
        try:
            geoserver_url = config['ckanext.publicamundi.vectorstorer.geoserver.url']
        except KeyError:
            pass

        try:
            mapserver_url = config['ckanext.publicamundi.vectorstorer.mapserver.url']
        except KeyError:
            pass
    else:
        # used by celery tasks
        try:
            geoserver_context = backend_context['geoserver_context']
            geoserver_url = geoserver_context['url'] if geoserver_context else None
        except KeyError:
            pass
        try:
            mapserver_context = backend_context['mapserver_context']
            mapserver_url = mapserver_context['url'] if mapserver_context else None
        except KeyError:
            pass
    
    if resource['format'] == 'wms':
        if geoserver_url and (geoserver_url in resource['wms_server']):
            return PUBLISHED_AT_GEOSERVER
        elif mapserver_url and (mapserver_url in resource['wms_server']):
            return PUBLISHED_AT_MAPSERVER
    elif resource['format'] == 'wfs':
        if geoserver_url and (geoserver_url in resource['wfs_server']):
            return PUBLISHED_AT_GEOSERVER
        elif mapserver_url and (mapserver_url in resource['wfs_server']):
            return PUBLISHED_AT_MAPSERVER

    return None
