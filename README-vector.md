Publicamundi Vector Plugin
==========================


Overview
--------

The `publicamundi_vector` plugin allows users to upload vector geospatial data, and store and publish through OGC services.


Installation
------------

**1.  Install required Debian packages**

Install compression-related libraries

    sudo apt-get install unzip unrar p7zip-full

Install GDAL libraries and Python bindings (at system-level):

    sudo apt-get install python-gdal   

**2.  Install plugin's requirements**

    pip install -r vector-requirements.txt


Configuration
-------------

**1.  Enable Vector Storer**

  This plugin requires `publicamundi_dataset` to be also enabled. To enable the plugin add this under `ckan.plugins` in the configuration file:
 
        ckan.plugins = ... publicamundi_dataset publicamundi_vector ...

    
**2.  Configure Plugin**

  The following should be set in the CKAN config:

        ckanext.publicamundi.vectorstorer.temp_dir = %(cache_dir)s/vectorstorer
        ckanext.publicamundi.vectorstorer.gdal_folder = (e.g. /usr/lib/python2.7/dist-packages)

Geoserver-specific configuration

        ckanext.publicamundi.vectorstorer.geoserver.url = (e.g. http://www.example.com/geoserver)
        ckanext.publicamundi.vectorstorer.geoserver.api_url = (e.g. http://geoserver.localdomain:8080/geoserver)
        ckanext.publicamundi.vectorstorer.geoserver.workspace = (e.g. CKAN)
        ckanext.publicamundi.vectorstorer.geoserver.username = (e.g. admin)
        ckanext.publicamundi.vectorstorer.geoserver.password = (e.g. geoserver)
        ckanext.publicamundi.vectorstorer.geoserver.datastore = (e.g. ckan_datastore_default)
        ckanext.publicamundi.vectorstorer.geoserver.reload_url = (optional e.g. http://geoserver.localdomain:5005/reload)

Geoserver workspace and datastore have to be created in advance. The datastore must be the same as the CKAN datastore database.

Mapserver-specific configuration

        ckanext.publicamundi.vectorstorer.mapserver.url = (e.g. http://ckan_services_server/cgi-bin/mapserv)
        ckanext.publicamundi.vectorstorer.mapserver.mapfile_folder = (e.g. /var/www/mapserv/mapfiles)
        ckanext.publicamundi.vectorstorer.mapserver.templates_folder = (e.g. /var/www/mapserv/templates)
    
If both mapserver and geoserver are both configured, default publishing server has to be specified:

        ckanext.publicamundi.vectorstorer.default_publishing_server= (e.g. mapserver)
    
If not set, `geoserver` will be used as the default publishing server.

**3.  Prepare Datastore**

  Enable the PostGis extension in the datastore database.

