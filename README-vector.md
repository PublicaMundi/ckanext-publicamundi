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

  The following should be set in the CKAN config :

        ckanext.publicamundi.vectorstorer.temp_dir = %(cache_dir)s/vectorstorer
        ckanext-vectorstorer.geoserver_url = (e.g. http://ckan_services_server/geoserver)
        ckanext-vectorstorer.geoserver_workspace = (e.g. CKAN)
        ckanext-vectorstorer.geoserver_admin = (e.g. admin)
        ckanext-vectorstorer.geoserver_password = (e.g. geoserver)
        ckanext-vectorstorer.geoserver_ckan_datastore = (e.g. ckan_datastore_default)
        ckanext-vectorstorer.gdal_folder = (e.g. /usr/lib/python2.7/dist-packages)

  Geoserver workspace and datastore have to be created in advance. The datastore must be the same as the CKAN datastore database.

**3.  Prepare Datastore**

  Enable the PostGis extension in the datastore database.

