"""
A collection of utility functions needed for the raster plugin
"""
import urllib as url
import fileinput
import os

import pylons.config as config
from gdal_to_gml import GDALToGmlConverter


class RasterUtil:
    """
    Static class that contains utility methods for the rasterimport ckan plugin
    """
    def __init__(self):
        # This class contains only static methods
        pass

    @staticmethod
    def get_path_to_public_folder():
        return os.path.dirname(os.path.realpath(__file__)) + "/../public/"

    @staticmethod
    def download_file_to_temp_directory(file_url, file_name):
        """
        Downloads a file from a given url and saves it to the /tmp folder

        :param file_url: string the url of the file
        :param file_name: string - the name of the file to be saved in /tmp
        :return: string - the complete path to the file
        """
        url_handle = url.urlopen(file_url)
        file_temp_path = RasterUtil.get_path_to_public_folder() + "/" + str(file_name) + ".raster"
        file_handle = open(file_temp_path, "wb")
        file_handle.write(url_handle.read())
        file_handle.close()
        return file_temp_path

    @staticmethod
    def write_gml_string_to_temp_file(gml, coverage_id):
        """
        Writes a gml string to a temporary file and returns the path to it

        :param gml: string - the gml string to be written to disk
        :param coverage_id: string - the coverage id or any unique identifier
        :return: string - the path to the file
        """
        file_temp_path = RasterUtil.get_path_to_public_folder() + "/" + str(coverage_id) + ".xml"
        file_handle = open(file_temp_path, "wb")
        file_handle.write(gml)
        file_handle.close()
        return file_temp_path

    @staticmethod
    def dataset_id_to_coverage_id(dataset_id):
        """
        Converts the id of a ckan dataset to a coverage id in a deterministic mode

        :param dataset_id: string - the id of the dataset (usually UUID format)
        :return: string - the generated coverage id
        """
        coverage_id = "Cov_" + dataset_id.replace("-", "_").replace(" ", "_")
        return coverage_id

    @staticmethod
    def get_wcst_url():
        """
        Returns the base url to the wcst service
        :return: the base url to the wcst service
        """
        return config.get("ckanext.publicamundi.rasterstorer.wcst_base_url", "").strip(' \t\n\r')

    @staticmethod
    def get_wms_url():
        """
        Returns the base url to the wms service
        :return: the base url to the wms service
        """
        return config.get("ckanext.publicamundi.rasterstorer.wms_base_url", "").strip(' \t\n\r')


    @staticmethod
    def get_gml_path_from_dataset(coverage_url, dataset_id):
        """
        Given a dataset that was inserted into ckan, it returns a gml file that can be served to WCST service

        :param coverage_url: string - the url to the dataset
        :param dataset_id: string - the id of the dataset
        :return: string - the local url to the generated gml file
        """
        coverage_id = RasterUtil.dataset_id_to_coverage_id(dataset_id)
        coverage_local_path = RasterUtil.download_file_to_temp_directory(coverage_url, coverage_id)
        if RasterUtil.is_gml(coverage_url):
            RasterUtil.replace_coverage_id_in_gml_file(coverage_local_path, coverage_id)
        else:
            converter = GDALToGmlConverter(coverage_local_path, coverage_id, coverage_url)
            gml_result = converter.to_gml()
            coverage_local_path = RasterUtil.write_gml_string_to_temp_file(gml_result, coverage_id)

        return coverage_local_path

    @staticmethod
    def replace_coverage_id_in_gml_file(file_path, new_coverage_id):
        """
        Replaces the coverage id of a given gml file with a given id. See http://stackoverflow.com/a/290494 for the explanation
        to this solution

        :param file_path: string - the file in which the operation takes place
        :param new_coverage_id: string - the gml_id to be given to the coverage
        """
        for line in fileinput.input(file_path, inplace=True):
            if line.find("gml:id=\"") != -1:
                old_coverage_id = line.split("gml:id=\"")[1].split("\"")[0]
                print line.replace(old_coverage_id, new_coverage_id),
            else:
                print line,

    @staticmethod
    def is_gml(coverage_url):
        """
        Returns True if a file is in GML format, false othewise. Note that this is not a conclusive method of determining
        this but works correctly as all other gdal formats have a different extension

        :param coverage_url: string - the url to the file to be checked
        :return: bool - the result of the check
        """
        return True if (coverage_url.endswith(".xml")) else False

