import urllib
from collections import OrderedDict
from pylons import config

import ckanext.publicamundi.storers.vector as vectorstorer

def get_wfs_output_formats(backend='geoserver'):
    return vectorstorer.wfs_output_formats.get(backend, {})

def url_for_wfs_feature_layer(service_endpoint, layer_name, output_format, srs):
    '''Build a WFS GetFeature request'''
    qs_params = OrderedDict([
        ('service', 'WFS'),
        ('version', '1.0.0'),
        ('request', 'GetFeature'),
        ('typeName', str(layer_name)),
        ('outputFormat', str(output_format)),
        ('srs', str(srs)),
    ])
    return service_endpoint + '?' + urllib.urlencode(qs_params)

def get_table_resource(pkg_dict, res_dict):
    '''Return the table resource on which a WMS/WFS is based on.
    '''
    
    workspace = config['ckanext.publicamundi.vectorstorer.geoserver.workspace']
    res_format = res_dict['format']
    
    if res_format == 'wfs':
        published_layer = res_dict['wfs_layer']
    elif res_format == 'wms':
        published_layer = res_dict['wms_layer']
    else:
        assert False, (
            'This helper can only be used for WMS/WFS vectorstorer resources')
    
    target_res = None
    if published_layer.startswith(workspace):
        rid = published_layer[len(workspace):].lstrip(':')
        target_res = next(r for r in pkg_dict['resources'] 
            if r['format'] == 'data_table' and r['id'] == rid)

    return target_res

    
