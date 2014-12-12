"""
Classes that transform a gdal supported file into a gml file
"""
import os
import magic


class GDALToGmlConverter:
    """
    Class to convert a GDAL supported file to GML

    Usage:
    <code>
    converter = GDALToGmlConverter("path/to/some/file", "someCoverageId", "file://mydata.tif")
    gml_string = converter.to_gml()
    </code>
    """

    def __init__(self, gdal_file_path, coverage_id, url_to_coverage_data):
        """
        Constructor for the class

        :param gdal_file_path: string - path to the file to be converted
        :param coverage_id: string - an id for this coverage
        :param url_to_coverage_data: string - an url pointing to a file that contains the coverage data;
        usually this is the same as the gdal_file_path. Please note that an url format is required
        (i.e. local files should be file://path)
        """
        import osgeo.gdal as gdal
        self.coverage_id = coverage_id
        self.url_to_coverage_data = url_to_coverage_data
        self.gdal_file_path = gdal_file_path
        self.gdal_dataset = gdal.Open(self.gdal_file_path)
        self.__init_templates()

    def __init_templates(self):
        """
        Initializes the GML template components
        """
        self.main_gml_template = open(self.MAIN_GML_TEMPLATE_PATH).read()
        self.offset_vector_template = open(self.OFFSET_VECTOR_TEMPLATE_PATH).read()
        self.range_type_template = open(self.RANGE_TYPE_TEMPLATE_PATH).read()

    def get_fields(self):
        """
        Returns the range type fields from a gdal dataset

        :return: a list of range type fields in gml format
        """
        import osgeo.gdal as gdal
        fields = []
        for i in range(1, self.gdal_dataset.RasterCount + 1):
            template = self.range_type_template
            band = self.gdal_dataset.GetRasterBand(i)

            # Add the null values to the template
            if band.GetNoDataValue() is not None:
                template = template.replace("$VarNillReason", "None")
                template = template.replace("$VarNillValues", """<swe:nilValues>
                        <swe:NilValues>
                            <swe:nilValue reason="">""" + str(band.GetNoDataValue()) + """</swe:nilValue>
                        </swe:NilValues>
                    </swe:nilValues>""")
            else:
                template = template.replace("$VarNillValues", "")

            # Add the color interpretation to the template
            if band.GetColorInterpretation() is not None:
                template = template.replace("$VarFieldName",
                                            gdal.GetColorInterpretationName(band.GetColorInterpretation()))
            else:
                template = template.replace("$VarFieldName", "")

            # We cannot extract this information yet and is not mandatory in GML so ommit it for the moment
            template = template.replace("$VarFieldDefinition", "")
            template = template.replace("$VarFieldDescription", "")

            # Add the units of measure to template
            if band.GetUnitType() is not None:
                template = template.replace("$VarUomCode", band.GetUnitType())
            else:
                template = template.replace("$VarUomCode", "")

            fields.append(template)

        return fields

    def get_center(self):
        """
        Returns the center of the created coverage

        :return: "0.0 0.0" as gdal only works with 2D images and petascope can automatically calculate it for such
        datasets we return a default value
        """
        geo = self.gdal_dataset.GetGeoTransform()
        # Petascope does not handle correctly importing from a non-zero center, but supports automatic calculation
        # As the center will be calculated automatically if 0,0 is provided to petascope we will use this method
        # If a different implementation will be used we should return (xgeo, ygeo)
        return str(geo[0]) + " " + str(geo[3])

    def get_offset_vectors(self):
        """
        Returns the offset vectors for the coverage calculated from the dataset

        :return: a list of offset vectors in gml format
        """
        offset_vectors = []

        # Create the offset vectors according to the gml standard
        offset_x = "0 " + str(self.gdal_dataset.GetGeoTransform()[1])
        offset_y = str(self.gdal_dataset.GetGeoTransform()[5] * -1) + " 0"

        # Fill the templates
        offset_vectors.append(self.offset_vector_template.replace("$VarGmlOffset", offset_x))
        offset_vectors.append(self.offset_vector_template.replace("$VarGmlOffset", offset_y))
        return offset_vectors

    def get_crs(self):
        """
        Returns the CRS associated with this dataset. If none is found, OGC/0/Index2D is returned

        :return: string - the CRS of the dataset
        """

        import osgeo.osr as osr
        wkt = self.gdal_dataset.GetProjection()
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromWkt(wkt)
        crs = self.DEFAULT_CRS
        if spatial_ref.GetAuthorityName(None) is not None:
            crs = spatial_ref.GetAuthorityName(None) + "/0/" + spatial_ref.GetAuthorityCode(None)

        return crs

    def get_mime(self):
        """
        Returns the mime type of the given gdal file

        :return: string - the mimetype of the file
        """
        mime_lib = magic.Magic(mime=True)
        mime = mime_lib.from_file(self.gdal_file_path)
        mime = "" if mime is None else mime
        return mime

    def to_gml(self):
        """
        Returns a GML representation of the given dataset in string format. Please note that as gdal does not offer all
        the relevant information needed to create a GML, several assumptions are made:
        - center of the coverage is defaulted to "0 0"
        - default CRS is OGC/0/Index2D

        :return: the gml representation of the dataset
        """
        gml_str = self.main_gml_template \
            .replace("$VarGmlId", self.coverage_id) \
            .replace("$VarSrsName", self.OPEN_GIS_URL + self.get_crs()) \
            .replace("$VarGridEnvelopeLow", "0 0") \
            .replace("$VarGridEnvelopeHigh",
                     str(self.gdal_dataset.RasterXSize) + " " + str(self.gdal_dataset.RasterYSize)) \
            .replace("$VarOriginGmlPos", self.get_center()) \
            .replace("$VarFileName", self.url_to_coverage_data) \
            .replace("$VarMimeType", self.get_mime()) \
            .replace("$VarFields", ' '.join(self.get_fields())) \
            .replace("$VarGmlOffsetVectors", self.get_offset_vectors()[0] + " " + self.get_offset_vectors()[1])

        return gml_str

    MAIN_GML_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates/gml_main_template.xml")
    OFFSET_VECTOR_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates/gml_offset_vector_template.xml")
    RANGE_TYPE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates/gml_range_type_template.xml")
    DEFAULT_CRS = "OGC/0/Index2D"
    OPEN_GIS_URL = "http://www.opengis.net/def/crs/"