import geojson
import shapely

def geojson_to_wkt(s):
    from shapely.geometry import shape
    g = shape(geojson.loads(s))
    return g.wkt

def geojson_to_wkb(s):
    from shapely.geometry import shape
    g = shape(geojson.loads(s))
    return g.wkb

def wkt_to_geojson(s):
    from shapely.wkt import loads as wkt_loads
    g = geojson.Feature(geometry=wkt_loads(s))
    return str(g.geometry)

