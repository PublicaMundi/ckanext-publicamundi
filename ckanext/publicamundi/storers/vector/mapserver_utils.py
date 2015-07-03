import os
import urlparse

MAP_PROJECTION = 4326
OWS_SRS_LIST = [4326, 2100, 3857, 32632]

mapscript = None
ogr = None
osr = None

class MapServerUtils:

    def __init__(self, vectorstorer):

        global mapscript
        mapscript = vectorstorer.mapscript
        global ogr
        ogr = vectorstorer.ogr
        global osr
        osr = vectorstorer.osr

    def load_mapfile(self, mapfile_path):
        map = mapscript.mapObj(mapfile_path)
        return map

    def create_mapfile_obj(self,mapfile_folder, mapserver_url, pkg_name):
        '''Creates a new mapfile. The new mapfile has the name of the package
        it was created from.'''
        map = mapscript.mapObj()

        # Set Map projection
        map.setProjection("init=epsg:%d" %(MAP_PROJECTION))
        map.setSize(256,256)

        ows_srs_val = " ".join("EPSG:{0}".format(srs) for srs in OWS_SRS_LIST)

        # Set WMS properties
        map.web.metadata.set("wms_title","WMS Service for dataset: %s" %(pkg_name))
        map.web.metadata.set("wms_enable_request","*")
        map.web.metadata.set("wms_srs", ows_srs_val)
        map.web.metadata.set("wms_onlineresource",mapserver_url)
        map.web.metadata.set("wms_format","image/png")
        map.web.metadata.set("wms_feature_info_mime_type","text/html")

        # Set WFS properties
        map.web.metadata.set("wfs_title","WFS Service for dataset: %s" %(pkg_name))
        map.web.metadata.set("wfs_enable_request","*")
        map.web.metadata.set("wfs_srs", ows_srs_val)
        map.web.metadata.set("wfs_onlineresource",mapserver_url)

        # Set mapfile symbolset
        symbolset_path = os.path.join(mapfile_folder,"symbols.sym")
        if not os.path.exists(symbolset_path):
            self._create_symbolset(symbolset_path)

        map.setSymbolSet(symbolset_path)

        return map

    def create_layer(self,
                     map,
                     resource_id,
                     layer,
                     layer_name,
                     geom_name,
                     srs,
                     srs_wkt,
                     db_params):
        ''' Creates a (postgis) layer object by the given params.'''

        new_layer = mapscript.layerObj()

        # Set layer name and title
        new_layer.name = "ckan_" + resource_id
        new_layer.tileitem = layer_name

        # Set layer connection and data query
        new_layer.connection = self._get_db_connection_string(db_params)
        new_layer.setConnectionType(mapscript.MS_POSTGIS,None)
        new_layer.data='the_geom from "%s" USING srid=%d USING unique _id' %( resource_id, srs)

        # Set layer type (Point, Polygon, etc)
        if geom_name in ["POLYGON","MULTIPOLYGON"]:
            new_layer.type=mapscript.MS_LAYER_POLYGON
        elif geom_name in ["POINT","MULTIPOINT"]:
            new_layer.type=mapscript.MS_LAYER_POINT
        elif geom_name in ["LINESTRING","MULTILINESTRING"]:
            new_layer.type=mapscript.MS_LAYER_LINE
        else:
            new_layer.type=mapscript.MS_SHAPE_NULL

        #Set layer extend and projection
        layer_extent= layer.GetExtent()

        new_layer.setExtent(
            layer_extent[0],layer_extent[2],
            layer_extent[1],layer_extent[3])

        new_layer.setWKTProjection(srs_wkt)

        # Set layer metadata
        new_layer.metadata.set('ows_title',layer_name)
        new_layer.metadata.set('ows_srs', str(srs))

        # Set layer status enabled
        new_layer.status = mapscript.MS_ON

        # Set a default style for layers based on geom_name
        classobj = mapscript.classObj()
        classobj.name="%s default style" %(new_layer.type)

        # Add class and style(s) to layer
        styleobj_array = self._get_default_mapserver_style( map,new_layer)
        for styleobj in styleobj_array:
            classobj.insertStyle(styleobj)

        new_layer.insertClass(classobj)

        return new_layer

    def create_mapscript_rect_obj(self, minx, miny, maxx, maxy):
        '''Returns a mapscript rectangle object.'''
        r_obj = mapscript.rectObj(
                    float(minx),float( miny),float( maxx),float( maxy))
        return r_obj

    def _get_db_connection_string(self, db_params):
        '''Returns an appropriate for mapfile database connection
        string.'''
        result = urlparse.urlparse(db_params)
        user = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        db_string = "dbname=%s host=%s user=%s password=%s" %(database, hostname, user, password)
        return db_string

    def _create_symbolset(self, symbolset_path):
        '''Creates a symbolset (containing the square symbol)
        and saves it as symbols.sym'''
        symbolset = mapscript.symbolSetObj()
        new_symbol = mapscript.symbolObj('square')
        line = mapscript.lineObj()
        line.add( mapscript.pointObj(0.0, 4.0))
        line.add( mapscript.pointObj(4.0, 4.0))
        line.add( mapscript.pointObj(4.0, 0.0))
        line.add( mapscript.pointObj(0.0, 0.0))
        line.add( mapscript.pointObj(0.0, 4.0))

        new_symbol.setPoints(line)
        new_symbol.filled = True
        symbolset.appendSymbol(new_symbol)
        symbolset.save(symbolset_path)

    def _get_default_mapserver_style(self, map, new_layer):
        ''' Returns an array of styles based on the geomerty
        type of the created layer'''

        styleobj_array = []

        # Line Geometry default styling
        if new_layer.type == mapscript.MS_LAYER_LINE:
            styleobj = mapscript.styleObj()
            styleobj.color.setHex("#0000FF")
            styleobj.size = 1
            styleobj_array.append(styleobj)

        # Polygon Geometry default styling
        elif new_layer.type == mapscript.MS_LAYER_POLYGON:
            styleobj = mapscript.styleObj()
            styleobj.color.setHex("#AAAAAA")
            styleobj.outlinecolor.setHex("#000000")
            styleobj.size = 1
            styleobj_array.append(styleobj)

        # Point Geometry default styling
        elif new_layer.type == mapscript.MS_LAYER_POINT:

            styleobj = mapscript.styleObj()
            styleobj.color.setHex("#FF0000")
            styleobj.setSymbolByName(map, 'square')
            styleobj.size = 6
            styleobj_array.append(styleobj)

        else:
            styleobj = mapscript.styleObj()
            styleobj.color.setHex('#0000ff')
            styleobj.width=3
            styleobj_array.append(styleobj)

        return styleobj_array

    def _calc_mapfile_extent(self, map):
        '''Returns the spatial extent of a map file in the following
        format : [minx, miny, maxx, maxy]'''

        # Create a memory vector layer to add each layer's extent
        # as a feature
        drv = ogr.GetDriverByName( 'Memory' )
        dst_ds = drv.CreateDataSource( 'temp_vector_for_extent' )

        ext_layer = dst_ds.CreateLayer("map_extent", geom_type=ogr.wkbPolygon)
        for layer_idx in map.getLayerOrder():

            # Create a polygon for each layer, from the bounding
            # box coordinates
            ring = ogr.Geometry(ogr.wkbLinearRing)
            layer_extent = map.getLayer(layer_idx).getExtent()
            ring.AddPoint(layer_extent.minx,layer_extent.miny)
            ring.AddPoint(layer_extent.maxx,layer_extent.miny)
            ring.AddPoint(layer_extent.maxx,layer_extent.maxy)
            ring.AddPoint(layer_extent.minx,layer_extent.maxy)
            ring.AddPoint(layer_extent.minx,layer_extent.miny)

            # reproject the geometry to default map projection
            ring_reprojected = self._reproject_geom_to_default_proj(ring,map.getLayer(layer_idx).getProjection() )

            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring_reprojected)

            featureDefn = ext_layer.GetLayerDefn()

            # create a new feature
            layer_ext_feat = ogr.Feature(featureDefn)

            # Set geometry
            layer_ext_feat.SetGeometry(poly)

            # Add new feature to output Layer
            ext_layer.CreateFeature(layer_ext_feat)

        extent = list(ext_layer.GetExtent())
        return extent[0], extent[2], extent[1], extent[3]

    def _reproject_geom_to_default_proj(self, geom, native_spatial_ref):
        '''Reprojects the geom from layer's native spatial reference
        system to the default projection of the map.'''
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromProj4(native_spatial_ref)

        # output SpatialReference
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(MAP_PROJECTION)

        # create the CoordinateTransformation
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

        geom.Transform(coordTrans)
        return geom