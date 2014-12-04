import urlparse
import os

from ckan.lib.base import BaseController, request
from ckan.logic import model
import ckan
import wcst
from raster_plugin_util import RasterUtil


class RasterImportController(BaseController):
    """
    Controller for interacting with WCST through ckan
    Two methods are expose:
    /api/raster/publish/{resource_id} - inserting the raster into rasdaman through WCST
    /api/raster/delete/{resource_id} - deleting the raster from rasdaman through WCST
    """

    def publish(self, resource_id):
        """
        Publishes a raster resource in WCST

        :param resource_id: String the id of the resource
        """
        base_url = "http://" + urlparse.urlparse(request.url).netloc + "/"
        resource = ckan.model.Session.query(model.Resource).get(resource_id)
        self.insert_coverage(resource.url, resource_id, base_url)

    def delete(self, resource_id):
        """
        Deletes the raster resource using WCST

        :param resource_id: String the id of the resource
        """
        self.delete_coverage(resource_id)

    @staticmethod
    def insert_coverage(coverage_url, dataset_id, base_url):
        """
        Inserts a coverage attached to a dataset into the WCST service

        :param coverage_url: string - url to the coverage to be inserted (can be in any gdal supported format + GML)
        :param dataset_id: string - the id of the dataset to which this coverage is attached to
        """

        coverage_local_path = RasterUtil.get_gml_path_from_dataset(coverage_url, dataset_id)
        gml_url = base_url + os.path.basename(coverage_local_path)

        # Execute the wcst insert request
        request = wcst.WCSTInsertRequest(gml_url)
        executor = wcst.WCSTExecutor(RasterUtil.get_wcst_url())
        response = executor.execute(request)

        wms_request = wcst.WMSFromWCSInsertRequest(response)
        wms_request.execute(RasterUtil.get_wms_url())
        # Cleanup
        os.remove(coverage_local_path)
        os.remove(coverage_local_path.replace(".xml", ".raster"))

        return response

    @staticmethod
    def delete_coverage(dataset_id):
        """
        Deletes a coverage attached to a dataset from the WCST service
        :param dataset_id: string - the id of the dataset to which this coverage is attached to
        """
        request = wcst.WCSTDeleteRequest(RasterUtil.dataset_id_to_coverage_id(dataset_id))
        executor = wcst.WCSTExecutor(RasterUtil.get_wcst_url())
        response = executor.execute(request)

        wms_request = wcst.WMSFromWCSDeleteRequest(response)
        wms_request.execute(RasterUtil.get_wms_url())
        return response
