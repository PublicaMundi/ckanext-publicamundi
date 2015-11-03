ckanext-publicamundi
====================

This is a CKAN extension that hosts various plugins needed for PublicaMundi project!

Install
-------

    pip install -r requirements.txt
    python setup.py develop
    paster publicamundi --config /path/to/development.ini setup


Update CKAN configuration
-------------------------

Edit your CKAN .ini configuration file (e.g. your `development.ini`) and activate the
plugins as usual. For now, the supported plugins are:

 * `publicamundi_dataset`: Provides validation logic, storage logic and ui controls for schema-following metadata (e.g. INSPIRE).
 * `publicamundi_multilingual_dataset`: Extend `publicamundi_dataset` to support multilingual metadata.
 * `publicamundi_package`: Provides synchronization of package metadata to other databases (e.g. to the integrated CSW service, through pycsw).
 * `publicamundi_vector`: Provide processing and services for vector-based spatial resources. See more at README-vector.md
 * `publicamundi_raster`: Provide processing and services for raster-based spatial resources. See more at README-raster.md 


Configure
---------

Here we cover some of the configuration settings for only basic plugins of `ckanext-publicamundi`. Settings which are specific to a _storer_ plugin (either 
`publicamundi_vector` or `publicamundi_raster`) are documented in their dedicated README file.

The most common settings are:

    # Specify which dataset types are enabled
    ckanext.publicamundi.dataset_types = ckan inspire foo
    
    # Indicate whether a more relaxed name pattern can be used for dataset names
    ckanext.publicamundi.validation.relax_name_pattern = true 
    
    # Specify a list of formats which should be considered as services (APIs)
    ckanext.publicamundi.api_resource_formats = wms wcs wfs csw

    # Add extra top-level (i.e not contained in schema) metadata fields. This is usually needed to provide 
    # a bridge to 3rd-party plugins that expect certain fields to be present (e.g. `spatial` from `spatial_metadata`).
    ckanext.publicamundi.extra_fields = spatial

    # Specify a list of pre-existing resource formats to be used as autocomplete suggestions
    ckanext.publicamundi.resource_formats = 
    # raster file formats 
        geotiff bitmap png jpeg
    # vector file formats
        shapefile sqlite gml kml
    # services, apis
       %(ckanext.publicamundi.api_resource_formats)s

    # Specify the path to pycsw configuration 
    ckanext.publicamundi.pycsw.config = %(here)s/pycsw.ini

    # Specify the endpoint under which CSW service is running (if it exists)
    ckanext.publicamundi.pycsw.service_endpoint = %(ckan.site_url)s/csw

Manage
------

The `publicamundi` command suite provides several subcommands to help managing the extension. Retreive a full list of available subcommands (along with their help):

    paster publicamundi --config /path/to/development.ini

To get help on a particular subcommand (e.g. `widget-info`):

    paster publicamundi --config /path/to/development.ini widget-info --help
    
Uninstall
---------

    paster publicamundi --config /path/to/development.ini cleanup

