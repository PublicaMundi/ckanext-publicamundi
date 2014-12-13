from urlparse import urlparse, urljoin


class WMSResource:

    FORMAT = 'wms'

    name_suffix = " (WMS)"
    _get_capabilities_url = "?service=WMS&version=1.3.0&request=GetCapabilities"
    _name = None
    _description = None
    _package_id = None
    _url = None
    _parent_resource_id = None
    _wms_server = None
    _wms_layer = None
    _rasterstorer_resource = True

    def __init__(
            self,
            package_id,
            layer_name,
            description,
            parent_resource_id,
            wms_server,
            wms_layer):
        self._package_id = package_id
        self._layer_name = layer_name
        self._name = layer_name + self.name_suffix
        self._description = description
        base_url = urlparse(wms_server)

        self._url = urljoin(base_url.netloc, self._get_capabilities_url)
        self._parent_resource_id = parent_resource_id
        self._wms_server = wms_server
        self._wms_layer = wms_layer

    def as_dict(self):
        resource = {
            "package_id": unicode(self._package_id),
            "url": self._wms_server + self._get_capabilities_url,
            "format": self.FORMAT,
            "parent_resource_id": self._parent_resource_id,
            'rasterstorer_resource': self._rasterstorer_resource,
            "wms_server": self._wms_server,
            "wms_layer": self._wms_layer,
            "name": self._name,
            "description": self._description
        }
        return resource


class WCSResource:

    FORMAT = 'wcs'

    name_suffix = " (WCS)"
    _get_capabilities_url = "?service=WCS&version=2.0.1&request=GetCapabilities"
    _name = None
    _description = None
    _package_id = None
    _url = None
    _parent_resource_id = None
    _wcs_server = None
    _wcs_coverage = None
    _rasterstorer_resource = True

    def __init__(
            self,
            package_id,
            layer_name,
            description,
            parent_resource_id,
            wcs_server,
            wcs_coverage):
        self._package_id = package_id
        self._layer_name = layer_name
        self._name = layer_name + self.name_suffix
        self._description = description
        base_url = urlparse(wcs_server)

        self._url = urljoin(base_url.netloc, self._get_capabilities_url)
        self._parent_resource_id = parent_resource_id
        self._wms_server = wcs_server
        self._wms_layer = wcs_coverage

    def as_dict(self):
        resource = {
            "package_id": unicode(self._package_id),
            "url": self._wms_server + self._get_capabilities_url,
            "format": self.FORMAT,
            "parent_resource_id": self._parent_resource_id,
            'rasterstorer_resource': self._rasterstorer_resource,
            "wcs_server": self._wms_server,
            "wcs_coverage": self._wms_layer,
            "name": self._name,
            "description": self._description
        }
        return resource