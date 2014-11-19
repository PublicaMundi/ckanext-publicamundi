from ckan.plugins import SingletonPlugin, implements, IDomainObjectModification,  IConfigurable, toolkit, IResourceUrlChange, IRoutes, IConfigurer,IActions
from ckan import model,logic

from ckan.common import _
import ckan
from ckanext.publicamundi.storers.vector import settings
from ckanext.publicamundi.storers.vector.lib import actions
from ckanext.publicamundi.storers.vector  import resource_actions
from pylons import config
from ckan.lib.dictization.model_dictize import resource_dictize


class VectorStorer(SingletonPlugin):
    STATE_DELETED='deleted'
    
    resource_delete_action= None
    resource_update_action=None
    
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)
    implements(IConfigurable, inherit=True)
    implements(IResourceUrlChange)
    implements(IDomainObjectModification, inherit=True)
    implements(IActions, inherit=True)
    
    def before_map(self, map):
	map.connect('edit_current_sld', '/dataset/{id}/resource/{resource_id}/edit_current_sld/{operation}',
            controller='ckanext.publicamundi.storers.vector.controllers.style:StyleController',
            action='edit_current_sld', id='{id}',resource_id='{resource_id}',operation='{operation}')
	map.connect('upload_sld', '/dataset/{id}/resource/{resource_id}/upload_sld/{operation}',
            controller='ckanext.publicamundi.storers.vector.controllers.style:StyleController',
            action='upload_sld', id='{id}',resource_id='{resource_id}',operation='{operation}')
	map.connect('vector_export', '/dataset/{id}/resource/{resource_id}/export/{operation}',
            controller='ckanext.publicamundi.storers.vector.controllers.export:ExportController',
            action='export',id='{id}',resource_id='{resource_id}',operation='{operation}')
	map.connect('search_epsg', '/api/search_epsg',
            controller='ckanext.publicamundi.storers.vector.controllers.export:ExportController',
            action='search_epsg')
	map.connect('vector_ingest', '/api/vector/ingest/{resource_id}',
            controller='ckanext.publicamundi.storers.vector.controllers.vector:VectorController',
            action='ingest',resource_id='{resource_id}')
	
	return map
    
    def get_actions(self):
        return {
            'resource_update': actions.new_resource_update,
            'resource_delete': actions.new_resource_delete,
        }
    def update_config(self, config):

        toolkit.add_public_directory(config, 'public')
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('public', 'ckanext-vectorstorer')    

    def notify(self, entity, operation=None):

        if isinstance(entity, model.resource.Resource):
	    
	    if operation==model.domain_object.DomainObjectOperation.new and entity.format.lower() in settings.VECTOR_FORMATS:
		#A new vector resource has been created
		#resource_actions.create_vector_storer_task(entity)
		res_dict = resource_dictize(entity, {'model': model})
		resource_actions.identify_resource(res_dict)
	    #elif operation==model.domain_object.DomainObjectOperation.deleted:
		##A vectorstorer resource has been deleted
		#resource_actions.delete_vector_storer_task(entity.as_dict())
	    
	    #elif operation is None:
		##Resource Url has changed
		
		#if entity.format.lower() in settings.SUPPORTED_DATA_FORMATS:
		    ##Vector file was updated
		    
		    #resource_actions.update_vector_storer_task(entity)
		    
		#else :
		    ##Resource File updated but not in supported formats
		 
		    #resource_actions.delete_vector_storer_task(entity.as_dict())
		    
	elif isinstance(entity, model.Package):
	    
	    if entity.state==self.STATE_DELETED:
		
		resource_actions.pkg_delete_vector_storer_task(entity.as_dict())