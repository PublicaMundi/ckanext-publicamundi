import datetime
import json
import geojson
import shapely

class JsonEncoder(json.JSONEncoder):
    '''Override default json.JSONEncoder behaviour so that it can serialize
    datetime objects
    '''
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)

def object_to_json(o, indent=None):
    return json.dumps(o, cls=JsonEncoder, indent=indent)

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

