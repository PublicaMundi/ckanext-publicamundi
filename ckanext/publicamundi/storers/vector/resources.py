from urlparse import urlparse, urljoin
from ckanext.publicamundi.storers.vector import settings

class WMSResource:
    name_extention=" WMS Layer"
    _get_capabilities_url="?service=WMS&request=GetCapabilities"
    _name= None
    _description= None
    _package_id= None
    _url= None
    _format= settings.WMS_FORMAT
    _parent_resource_id=None
    _wms_server= None
    _wms_layer= None
    _vectorstorer_resource= True
    
    def __init__(self,package_id, name, description, parent_resource_id, wms_server,wms_layer):
	self._package_id=package_id
	self._name=name + self.name_extention
	self._description=description
	base_url = urlparse(wms_server)

	self._url=urljoin( base_url.netloc,self._get_capabilities_url)
	self._parent_resource_id=parent_resource_id
	self._wms_server=wms_server
	self._wms_layer=wms_layer
	
	
    def get_as_dict(self):
	resource = {
	  "package_id":unicode(self._package_id),
	  "url":self._wms_server + self._get_capabilities_url,
	  "format":self._format,
	  "parent_resource_id":self._parent_resource_id,
	  'vectorstorer_resource': self._vectorstorer_resource,
	  "wms_server": self._wms_server,
	  "wms_layer": self._wms_layer,
	  "name":self._name,
	  "description": self._description }
	
	return resource
	
class DBTableResource:
    name_extention=" Data Preview"
    _name= None
    _description= None
    _package_id= None
    _url= None
    _format= settings.DB_TABLE_FORMAT
    _parent_resource_id=None
    _geometry= None
    _vectorstorer_resource= True
    
    def __init__(self,package_id, name, description, parent_resource_id, url, geometry):
	self._package_id=package_id
	self._name=name + self.name_extention
	self._description=description
	self._url=url
	self._parent_resource_id=parent_resource_id
	self._geometry=geometry
	
	
    def get_as_dict(self):
	resource = {
	  "package_id":unicode(self._package_id),
	  "url":self._url,
	  "format":self._format,
	  "parent_resource_id":self._parent_resource_id,
	  "geometry":self._geometry,
	  'vectorstorer_resource': self._vectorstorer_resource,
	  "name":self._name,
	  "description": self._description }
	
	return resource
	
	
	
	
	
	
	
	