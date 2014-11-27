ckanext-publicamundi
====================
-- stratiot rep

This is a CKAN extension that hosts various plugins needed for PublicaMundi project!

Install
-------

    pip install -r requirements.txt
    python setup.py develop
    paster publicamundi-setup --config /path/to/development.ini


Update CKAN configuration
-------------------------

Edit your CKAN .ini configuration file (e.g. your `development.ini`) and activate the
plugins as usual. For now, the supported plugins are:

 * `publicamundi_dataset`: Provides validation logic, storage logic and ui controls for metadata described in alternative schemata (e.g. INSPIRE).
 * `publicamundi_dataset_with_spatial`: Extends `publicamundi_dataset` by providing a bridge to `spatial_metadata` plugin: recognizes the `spatial` extra field. 
 * `publicamundi_package`: Provides synchronization of package metadata to other databases (e.g. to the intergrated CSW service).


Manage
------

The `publicamundi` command suite provides several subcommands to help managing the extension. Retreive a full list of available subcommands (along with their help):

    paster publicamundi --config /path/to/development.ini

To get help on a particular subcommand (e.g. `widget-info`):

    paster publicamundi --config /path/to/development.ini widget-info --help
    
Uninstall
---------

    paster publicamundi-cleanup --config /path/to/development.ini

