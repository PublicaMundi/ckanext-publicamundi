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

 * `publicamundi_dataset`: Provides validation logic, storage logic and UI controls for metadata following non-core (e.g. INSPIRE) metadata schemata.
  schemata.
 * `publicamundi_package`: Provides event handlers to sync your package metadata to other
    databases (e.g. to the intergrated CSW service).

Uninstall
---------

    paster publicamundi-cleanup --config /path/to/development.ini

