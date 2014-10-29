ckanext-publicamundi
====================

This is a CKAN extension that hosts various plugins needed for PublicaMundi project!

Install
-------

    python setup.py develop
    paster publicamundi-setup --config /path/to/development.ini

Update CKAN configuration
-------------------------

Edit your CKAN .ini configuration file (e.g. your `development.ini`) and activate the
plugins as usual. For now, the supported plugins are:

 * `publicamundi_dataset`: Provides validation logic, storage logic and ui controls for metadata following arbitrary (e.g. INSPIRE) metadata schemata.
  schemata.
 * `publicamundi_dataset_with_spatial`: Extends `publicamundi_dataset` by providing a bridge to `spatial_metadata` plugin brought by ckanext-spatial (recognizes the `spatial` extra field). 
 * `publicamundi_package`: Provides synchronization of package metadata to other databases (e.g. to the intergrated CSW service).

Uninstall
---------

    paster publicamundi-cleanup --config /path/to/development.ini

