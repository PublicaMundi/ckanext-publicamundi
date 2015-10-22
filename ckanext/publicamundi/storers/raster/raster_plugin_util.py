"""
A collection of utility functions needed for the raster plugin
"""
import urllib2
import urllib
import json
import fileinput
import os
import shutil
import logging
from resources import WCSResource, WMSResource
import errno


import wcst

from gdal_to_gml import GDALToGmlConverter


log = logging.getLogger(__name__)


class RasterUtil:
    """
    Static class that contains utility methods for the rasterimport ckan plugin
    """

    def __init__(self, context, logger):
        self.log = logger
        self.path_to_public_folder = context['temp_folder'].strip(' \t\n\r')
        self.url = context['url'].strip(' \t\n\r')
        self.wcst_url = context['wcst_base_url'].strip(' \t\n\r')
        self.wms_url = context['wms_base_url'].strip(' \t\n\r')
        self.resource_dict = context['resource_dict']
        self.api_key = context['user_api_key'].strip(' \t\n\r')
        self.site_url = context['site_url'].strip(' \t\n\r')
        self.coverage_id = self.resource_id_to_coverage_id()
        self.resource_temp_folder, self.resource_path, self.url_component = self.get_path_to_resource_files()
        self.gml_path = self.get_path_to_gml_file()
        self.gml_url = self.site_url + self.url_component + "/" + self.coverage_id + ".xml"
        self.resource_url = self.site_url + self.url_component + "/" + self.coverage_id + ".raster"
        pass

    def get_path_to_public_folder(self):
        return self.path_to_public_folder.strip(' \t\n\r')

    def download_resource(self):
        """
        Downloads the HTTP resource specified in resource-url and saves it under the public folder
        """
        self.log.info("[Raster_DownloadResource] Downloading resource %s from %s to: %s" % (self.resource_dict['id'],
                                                                                            self.resource_dict['url'],
                                                                                            self.resource_path))

        resource_url = urllib2.unquote(self.resource_dict['url'])
        is_upload = self.resource_dict.get('url_type', '') == 'upload'
        # Prepare download request

        download_request = urllib2.Request(resource_url)
        if is_upload:
            download_request.add_header('Authorization', self.api_key)

        # Perform request, handle errors
        try:
            download_response = urllib2.urlopen(download_request)
        except urllib2.HTTPError as ex:
            self.delete_temp()
            try:
                detail = ex.read(128)
            except IOError as ex:
                detail = 'n/a'
            raise CannotDownload(
                'Failed to download %s: %s: %s' % (resource_url, ex, detail))
        except urllib2.URLError as ex:
            self.delete_temp()
            raise CannotDownload(
                'Failed to download %s: %s' % (resource_url, ex))

        # Save downloaded resource in a local file
        with open(self.resource_path, 'wb') as ofp:
            ofp.write(download_response.read())
            ofp.close()
        self.log.info("[Raster_DownloadResource] Success!")

    def delete_temp(self):
        """
        Deletes the temporary folder in which the raw resource was kept
        """
        shutil.rmtree(self.resource_temp_folder)

    def get_path_to_resource_files(self):
        """
        Returns the path to the directory in which the resource is saved and the path to the actual resource
        :return:  the temporary folder path for this resource and the resource path
        """
        temp_folder = os.path.join(self.get_path_to_public_folder(), self.resource_dict['id'])
        try:
            os.makedirs(temp_folder)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(temp_folder):
                pass
        filename = "Cov_" + self.resource_dict['id'].replace("-", "_").replace(" ", "_") + ".raster"
        url_component = self.resource_dict['id']
        path = os.path.join(temp_folder, filename)
        return temp_folder, path, url_component

    def get_path_to_gml_file(self):
        """
        Returns the path to the gml file to be submitted to petascope
        :return:
        """
        filename = "Cov_" + self.resource_dict['id'].replace("-", "_").replace(" ", "_") + ".xml"
        path = os.path.join(self.resource_temp_folder, filename)
        return path

    def write_gml_string_to_temp_file(self, gml):
        """
        Writes a gml string to a temporary file and returns the path to it

        :param gml: string - the gml string to be written to disk
        """
        file_handle = open(self.gml_path, "wb")
        file_handle.write(gml)
        file_handle.close()

    def resource_id_to_coverage_id(self):
        """
        Converts the id of a ckan dataset to a coverage id in a deterministic mode

        :return: string - the generated coverage id
        """
        coverage_id = "Cov_" + self.resource_dict['id'].replace("-", "_").replace(" ", "_")
        return coverage_id

    def get_gml_url_from_resource(self):
        """
        Given a resource that was inserted into ckan, it returns a gml url that can be served to WCST service
        """
        self.log.info("[Raster_GeneratingGml] Generating gml from file at %s with coverage_id %s and resource_url %s" %
                      (self.gml_path, self.coverage_id, self.resource_url))
        if self.is_gml():
            self.replace_coverage_id_in_gml_file()
        else:
            converter = GDALToGmlConverter(self.resource_path, self.coverage_id, self.resource_url)
            gml_result = converter.to_gml()
            self.write_gml_string_to_temp_file(gml_result)
        self.log.info("[Raster_GeneratingGml] Success!")
        return self.gml_url

    def replace_coverage_id_in_gml_file(self):
        """
        Replaces the coverage id of a given gml file with a given id. See http://stackoverflow.com/a/290494 for the
        explanation
        to this solution
        """
        for line in fileinput.input(self.gml_path, inplace=True):
            if line.find("gml:id=\"") != -1:
                old_coverage_id = line.split("gml:id=\"")[1].split("\"")[0]
                print line.replace(old_coverage_id, self.coverage_id),
            else:
                print line,

    def is_gml(self):
        """
        Returns True if a file is in GML format, false othewise. Note that this is not a conclusive method of
        determining this but works correctly as all other gdal formats have a different extension

        :return: bool - the result of the check
        """
        return True if (self.resource_path.endswith(".xml")) else False

    def insert_coverage(self):
        """
        Inserts a coverage attached to a dataset into the WCST service
        :return the name of the layer / coverage
        """
        gml_url = self.get_gml_url_from_resource()
        self.log.info("[Raster_InsertCoverage]Executing WCST request of %s (path %s) to %s" %
                      (self.gml_url, self.gml_path, self.wcst_url))
        # Execute the wcst insert request
        request = wcst.WCSTInsertRequest(gml_url)
        executor = wcst.WCSTExecutor(self.wcst_url)
        response = executor.execute(request)
        self.log.info("[Raster_InsertCoverage]Success!")

        # Insert into wms
        self.log.info("[Raster_InsertCoverage]Executing WMST request of coverage %s to %s" % (response, self.wms_url))
        wms_request = wcst.WMSFromWCSInsertRequest(response)
        wms_request.execute(self.wms_url)
        self.log.info("[Raster_InsertCoverage]Success!")

        return response

    def delete_coverage(self):
        """
        Deletes a coverage attached to a dataset from the WCST service
        """
        self.log.info("[Raster_DeleteCoverage]Deleting %s from WCS at %s" % (self.coverage_id, self.wcst_url))
        request = wcst.WCSTDeleteRequest(self.coverage_id)
        executor = wcst.WCSTExecutor(self.wcst_url)
        executor.execute(request)
        self.log.info("[Raster_DeleteCoverage]Success!")

        self.log.info("[Raster_DeleteCoverage]Deleting %s from WMS at %s" % (self.coverage_id, self.wms_url))
        wms_request = wcst.WMSFromWCSDeleteRequest(self.coverage_id)
        wms_request.execute(self.wms_url)
        self.log.info("[Raster_DeleteCoverage]Success!")

    def check_wms_layer_exists(self):
        service_call = self.wms_url + "?service=WMS&version=1.3.0&request=GetCapabilities"
        self.log.info("[Raster_CheckWMSLayer]Checking if layer %s exists in %s" % (self.coverage_id, service_call))
        response = urllib2.urlopen(service_call).read()
        if self.coverage_id in response:
            return True
        else:
            return False

    def check_wcs_coverage_exists(self):
        """
        Checks if the coverage of this context was imported in wcs
        :return: true if so, false otherwise
        """
        service_call = self.wcst_url + "?service=WCS&acceptversions=2.0.1&request=GetCapabilities"
        self.log.info("[Raster_CheckWCSLayer]Checking if coverage %s exists in %s", self.coverage_id, service_call)
        response = urllib2.urlopen(service_call).read()
        if self.coverage_id in response:
            return True
        else:
            return False

    def check_import_successful(self):
        """
        Checks if the coverage of this context was imported in wms
        :return: true if so, false otherwise
        """
        try:
            if self.check_wms_layer_exists() and self.check_wcs_coverage_exists():
                self.log.info("[Raster_CheckSuccess] %s was found in both WCS and WMS" % self.coverage_id)
            else:
                raise CannotPublishRaster("Failed to import %s" % self.coverage_id)
        except Exception as ex:
            if isinstance(ex, CannotPublishRaster):
                raise ex
            else:
                raise CannotPublishRaster("Failed to import %s. Error message: %s" % (self.coverage_id, ex.message))

    def invoke_api_resource_action(self, resource, action):
        """
        Calls the api for resource manipulation
        :param resource: the resource to be manipulated
        :param action: the action to be taken
        :return: the created resource
        """
        data_string = urllib.quote(json.dumps(resource))
        request = urllib2.Request(self.site_url + 'api/action/' + action)
        request.add_header('Authorization', self.api_key)
        response = urllib2.urlopen(request, data_string)
        created_resource = json.loads(response.read())['result']
        return created_resource

    def add_wms_resource(self):
        """
        Creates a wms resource
        """
        wms_resource = WMSResource(
            self.resource_dict['package_id'],
            self.coverage_id,
            self.resource_dict['description'],
            self.resource_dict['id'],
            self.url,
            self.coverage_id,
            self.resource_dict['name'])
        created_wms_resource = self.invoke_api_resource_action(wms_resource.as_dict(), 'resource_create')

    def add_wcs_resource(self):
        """
        Creates a wcs resource
        """
        wms_resource = WCSResource(
            self.resource_dict['package_id'],
            self.coverage_id,
            self.resource_dict['description'],
            self.resource_dict['id'],
            self.url,
            self.coverage_id,
            self.resource_dict['name'])
        created_wcs_resource = self.invoke_api_resource_action(wms_resource.as_dict(), 'resource_create')

    def finalize(self):
        """
        Finalizes the import
        """
        self.log.info("[Raster_Finalizing] %s is being finalized" % self.resource_dict['id'])
        urllib.urlopen(self.site_url + "api/raster/finalize/" + self.resource_dict['id']).read()
        self.log.info("[Raster_Finalizing]Success!")

    def cleanup(self):
        """
        Deletes the working directory
        """
        self.delete_temp()


class CannotDownload(RuntimeError):
    pass


class CannotPublishRaster(RuntimeError):
    pass
