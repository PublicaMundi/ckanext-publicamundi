# CKAN Raster Importer

## Description

Extension that allows raster files to be imported into a WCST service.
The extension allows any gdal raster formats (GeoTIFF, JPEG2000 etc) and GML raster files.

## Configuration

You **need** to set the *wcst_base_url* and *wms_base_url* variables in your ckan main config file for this plugin to work. The value has to be an url pointing
to a working WCST service.

Example:
`ckanext.rasterimport.wcst_base_url = http://localhost/wcst`
`ckanext.publicamundi.rasterstorer.wcst_base_url = http://localhost/wcst`
`ckanext.publicamundi.rasterstorer.wms_base_url = http://localhost/wms`


## Dependencies

This extension requires the following pythong packages:

*	python-magic
*	GDAL (please note that the installation is currently broken)

