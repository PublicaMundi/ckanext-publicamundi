# CKAN Raster Importer

## Description

Extension that allows raster files to be imported into a WCST service.
The extension allows any gdal raster formats (GeoTIFF, JPEG2000 etc) and GML raster files.

## Configuration

You **need** to set the *wcst_base_url*, *wms_base_url*, *temp_dir* and *gdal_folder* variables in your ckan main config file for this plugin to work. 

Example:
`ckanext.publicamundi.rasterstorer.wcst_base_url=http://myRasdamanMachine/rasdaman/ows`
`ckanext.publicamundi.rasterstorer.wms_base_url=http://myRasdamanMachine/rasdaman/ows/wms13`
`ckanext.publicamundi.rasterstorer.temp_dir = %(cache_dir)s/rasterstorer`
`ckanext.publicamundi.rasterstorer.gdal_folder = /usr/lib/python2.7/dist-packages`
`ckanext.publicamundi.rasterstorer.wcst_import_url = http://imyRasdamanMachine:42000`


## Dependencies

This extension requires the following pythong packages:

*	python-magic
*	GDAL (please note that the installation is currently broken)

