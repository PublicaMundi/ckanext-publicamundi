from urlparse import urlparse, urljoin


class WMSResource:
    
    FORMAT = 'wms'
    
    name_extention = " (WMS)"
    _get_capabilities_url = "?service=WMS&request=GetCapabilities"
    _name = None
    _description = None
    _package_id = None
    _url = None
    _parent_resource_id = None
    _wms_server = None
    _wms_layer = None
    _vectorstorer_resource = True

    def __init__(
            self,
            package_id,
            name,
            description,
            parent_resource_id,
            wms_server,
            wms_layer):
        self._package_id = package_id
        self._name = name + self.name_extention
        self._description = description
        base_url = urlparse(wms_server)

        self._url = urljoin(base_url.netloc, self._get_capabilities_url)
        self._parent_resource_id = parent_resource_id
        self._wms_server = wms_server+"/wms"
        self._wms_layer = wms_layer

    def get_as_dict(self):
        resource = {
            "package_id": unicode(self._package_id),
            "url": self._wms_server + self._get_capabilities_url,
            "format": self.FORMAT,
            "parent_resource_id": self._parent_resource_id,
            'vectorstorer_resource': self._vectorstorer_resource,
            "wms_server": self._wms_server,
            "wms_layer": self._wms_layer,
            "name": self._name,
            "description": self._description}

        return resource


class DBTableResource:

    FORMAT = 'data_table'

    name_extention = " (Data)"
    _name = None
    _description = None
    _package_id = None
    _url = None
    _parent_resource_id = None
    _geometry = None
    _vectorstorer_resource = True

    def __init__(
            self,
            package_id,
            name,
            description,
            parent_resource_id,
            url,
            geometry):
        self._package_id = package_id
        self._name = name + self.name_extention
        self._description = description
        self._url = url
        self._parent_resource_id = parent_resource_id
        self._geometry = geometry

    def get_as_dict(self):
        resource = {
            "package_id": unicode(self._package_id),
            "url": self._url,
            "format": self.FORMAT,
            "parent_resource_id": self._parent_resource_id,
            "geometry": self._geometry,
            'vectorstorer_resource': self._vectorstorer_resource,
            "name": self._name,
            "description": self._description}

        return resource

class WFSResource:
    
    FORMAT = 'wfs'
    
    name_extention = " (WFS)"
    _get_capabilities_url = "?service=WFS&request=GetCapabilities"
    _name = None
    _description = None
    _package_id = None
    _url = None
    _parent_resource_id = None
    _wfs_server = None
    _wfs_layer = None
    _vectorstorer_resource = True

    def __init__(
            self,
            package_id,
            name,
            description,
            parent_resource_id,
            wfs_server,
            wfs_layer):
        self._package_id = package_id
        self._name = name + self.name_extention
        self._description = description
        base_url = urlparse(wfs_server)

        self._url = urljoin(base_url.netloc, self._get_capabilities_url)
        self._parent_resource_id = parent_resource_id
        self._wfs_server = wfs_server+"/wfs"
        self._wfs_layer = wfs_layer

    def get_as_dict(self):
        resource = {
            "package_id": unicode(self._package_id),
            "url": self._wfs_server + self._get_capabilities_url,
            "format": self.FORMAT,
            "parent_resource_id": self._parent_resource_id,
            'vectorstorer_resource': self._vectorstorer_resource,
            "wfs_server": self._wfs_server,
            "wfs_layer": self._wfs_layer,
            "name": self._name,
            "description": self._description}

        return resource
