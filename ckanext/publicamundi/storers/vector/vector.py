import psycopg2

import ckanext.publicamundi.storers.vector as vectorstorer
from ckanext.publicamundi.storers.vector import db_helpers


SHAPEFILE = 'ESRI Shapefile'
KML = 'KML'
GEOJSON = 'GeoJSON'
GML = 'GML'
GPX = 'GPX'
CSV = 'CSV'
XLS = 'XLS'
SQLITE = 'SQLite'
GEOPACKAGE = 'GPKG'


class DatasourceException(Exception):
    pass


class Vector:
    _check_for_conversion = False
    default_epsg = -1
    gdal_driver = None

    def __init__(
            self,
            gdal_driver,
            file_path,
            encoding=None,
            db_conn_params=None):
        self.gdal_driver = gdal_driver
        self.encoding = encoding
        self.db_conn_params = db_conn_params
        driver = vectorstorer.ogr.GetDriverByName(gdal_driver)
        self.dataSource = driver.Open(file_path, 0)
        if self.dataSource is None:
            raise DatasourceException('Could not open %s' % file_path)

    def get_layer_count(self):
        return self.dataSource.GetLayerCount()

    def get_layer(self, layer_idx):
        return self.dataSource.GetLayer(layer_idx)

    def handle_layer(self, layer, geom_name, table_name, srs, layer_encoding):
        featureCount = layer.GetFeatureCount()
        layerDefinition = layer.GetLayerDefn()
        self._db = db_helpers.DB(self.db_conn_params)
        fields = self._get_layer_fields(layerDefinition)
        layer.ResetReading()
        feat = layer.GetNextFeature()
        feat_geom = feat.GetGeometryRef()
        coordinate_dimension = feat_geom.GetCoordinateDimension()
        layer.ResetReading()
        self._db.create_table(
            table_name,
            fields,
            geom_name,
            srs,
            coordinate_dimension)
        self.write_to_db(table_name, layer, srs, geom_name, layer_encoding)

    def get_SRS(self, layer):
        if not layer.GetSpatialRef() is None:
            prj = layer.GetSpatialRef().ExportToWkt()
            srs_osr = vectorstorer.osr.SpatialReference()
            srs_osr.ImportFromESRI([prj])
            epsg = srs_osr.GetAuthorityCode(None)
            if epsg is None or epsg == 0:
                epsg = self.default_epsg
            return epsg
        else:
            return self.default_epsg

    def _get_layer_fields(self, layerDefinition):
        fields = ''
        for i in range(layerDefinition.GetFieldCount()):
            fname = layerDefinition.GetFieldDefn(i).GetName()
            ftype = layerDefinition.GetFieldDefn(i).GetType()
            if ftype == 0:
                fields += ',' + (fname + ' ' + 'integer')
            elif ftype == 1:
                fields += ',' + (fname + ' ' + 'integer[]')
            elif ftype == 2:
                fields += ',' + (fname + ' ' + 'real')
            elif ftype == 3:
                fields += ',' + (fname + ' ' + 'real[]')
            elif ftype == 4:
                fields += ',"' + (fname + '" ' + 'varchar')
            elif ftype == 5:
                fields += ',"' + (fname + '" ' + 'varchar[]')
            elif ftype == 6:
                fields += ',' + (fname + ' ' + 'varchar')
            elif ftype == 7:
                fields += ',' + (fname + ' ' + 'varchar[]')
            elif ftype == 8:
                fields += ',' + (fname + ' ' + 'bytea')
            elif ftype == 9:
                fields += ',' + (fname + ' ' + 'date')
            elif ftype == 10:
                fields += ',' + (fname + ' ' + 'time without time zone')
            elif ftype == 11:
                fields += ',' + (fname + ' ' + 'timestamp without time zone')

        return fields

    def get_geometry_name(self, layer):
        geometry_names = []
        for feat in layer:
            if not feat:
                continue
            feat_geom = feat.GetGeometryRef().GetGeometryName()
            if feat_geom not in geometry_names:
                geometry_names.append(feat_geom)

        geometry_name = None
        if len(geometry_names) == 1:
            return geometry_names[0]
        if len(geometry_names) == 2:
            multi_geom = None
            simple_geom = None
            for gname in geometry_names:
                gname_upp = gname.upper()
                if 'MULTI' in gname_upp:
                    multi_geom = gname_upp
                else:
                    simple_geom = gname_upp

            if multi_geom and simple_geom:
                if multi_geom.split('MULTI')[1] == simple_geom:
                    self._check_for_conversion = True
                    geometry_name = multi_geom
                    return geometry_name
            else:
                return 'GEOMETRY'
        elif len(geometry_names) > 2:
            return 'GEOMETRY'

    def get_sample_data(self, layer):
        feat_data = {}
        layer.ResetReading()
        for feat in layer:
            if not feat:
                continue

            for y in range(feat.GetFieldCount()):
                layerDefinition = layer.GetLayerDefn()
                field_name = layerDefinition.GetFieldDefn(y).GetName()
                feat_data[field_name] = feat.GetField(y)
            feat_data['geom'] = str(feat.GetGeometryRef())
            break
        return feat_data

    def write_to_db(self, table_name, layer, srs, layer_geom_name, layer_encoding):
        i = 0
        for feat in layer:
            feature_fields = '%s,' % i
            i = i + 1
            if not feat:
                continue
            for y in range(feat.GetFieldCount()):
                if not feat.GetField(y) is None:
                    if layer.GetLayerDefn().GetFieldDefn(y).GetType() in (4, 9, 10, 11):
                        field_value = str(
                            feat.GetField(y).decode(
                                layer_encoding,
                                'replace').encode('utf8'))
                        feature_fields += psycopg2.extensions.adapt(
                            field_value).getquoted().decode('utf-8') + ','
                    else:
                        feature_fields += str(feat.GetField(y)) + ','
                else:
                    feature_fields += 'NULL,'

            convert_to_multi = False
            if self._check_for_conversion:
                convert_to_multi = self.needs_conversion_to_multi(
                    feat,
                    layer_geom_name)
            self._db.insert_to_table(
                table_name,
                feature_fields,
                feat.GetGeometryRef(),
                convert_to_multi,
                srs)

        self._db.create_spatial_index(table_name)
        self._db.commit_and_close()

    def needs_conversion_to_multi(self, feat, layer_geom_name):
        if not feat.GetGeometryRef().GetGeometryName() == layer_geom_name:
            return True
        else:
            return False
