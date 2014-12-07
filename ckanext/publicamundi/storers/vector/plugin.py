import logging
from pylons import config

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.model as model

import ckanext.publicamundi.storers.vector as vectorstorer
from ckanext.publicamundi.storers.vector import resource_actions
from ckanext.publicamundi.storers.vector.resources import (
    DBTableResource, WMSResource) 
from ckanext.publicamundi.storers.vector.lib.template_helpers import (
    get_wfs_output_formats, url_for_wfs_feature_layer, get_table_resource)

log = logging.getLogger(__name__)

class VectorStorer(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IResourceUrlChange)
    p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.ITemplateHelpers)

    # IRoutes

    def before_map(self, map):
        controllers_base = "ckanext.publicamundi.storers.vector.controllers."
        styleController = (controllers_base + "style:StyleController")
        exportController = (controllers_base + "export:ExportController")
        vectorController = (controllers_base + "vector:VectorController")

        map.connect(
            'edit_current_sld',
            '/dataset/{id}/resource/{resource_id}/edit_style/{operation}',
            controller=styleController,
            action='edit_current_sld', id='{id}', resource_id='{resource_id}',
            operation='{operation}')

        map.connect(
            'upload_sld',
            '/dataset/{id}/resource/{resource_id}/upload_sld/{operation}',
            controller=styleController,
            action='upload_sld',
            id='{id}',
            resource_id='{resource_id}',
            operation='{operation}')

        map.connect(
            'vector_export',
            '/dataset/{id}/resource/{resource_id}/export/{operation}',
            controller=exportController,
            action='export',
            id='{id}',
            resource_id='{resource_id}',
            operation='{operation}')

        map.connect(
            'search_epsg',
            '/api/publicamundi/search_epsg',
            controller=vectorController,
            action='search_epsg')

        map.connect(
            'vector_ingest',
            '/api/publicamundi/vector/ingest/{resource_id}',
            controller=vectorController,
            action='ingest',
            resource_id='{resource_id}')

        return map

    # IActions
    
    def get_actions(self):
        '''Provide actions for the Action Api.
        
        So far, we replace 1 core action, so that:
         * resource_update: Maintains vectorstorer-specific resource metadata.
        
        '''
        
        # Fixme: Use another way to achieve the above, avoid patching core actions!
        # Under CKAN 2.2.x this will result in infinite recursion.
        
        # Define replacements for actions
        
        _resource_update = toolkit.get_action('resource_update')
        
        def resource_update(context, data_dict):
            resource = model.Session.query(model.Resource).get(data_dict['id']).as_dict()
            if 'vectorstorer_resource' in resource:
                data_dict['vectorstorer_resource'] = resource['vectorstorer_resource']
                if resource['format'].lower() == WMSResource.FORMAT:
                    data_dict['parent_resource_id'] = resource['parent_resource_id']
                    data_dict['wms_server'] = resource['wms_server']
                    data_dict['wms_layer'] = resource['wms_layer']
                if resource['format'].lower() == DBTableResource.FORMAT:
                    data_dict['parent_resource_id'] = resource['parent_resource_id']
                    data_dict['geometry'] = resource['geometry']
                if not data_dict['url'] == resource['url']:
                    raise toolkit.ValidationError(
                        'You cant upload a file to a %s resource.' % (resource['format']))
            return _resource_update(context, data_dict)

        # Register actions
        
        return {
            #'resource_update': resource_update,
        }

    ## ITemplateHelpers interface ##

    def get_helpers(self):
        return {
            'vectorstorer_wfs_output_formats': get_wfs_output_formats,
            'vectorstorer_wfs_feature_url': url_for_wfs_feature_layer,
            'vectorstorer_table_resource': get_table_resource,
        }

    # IConfigurer

    def update_config(self, config):

        # Configure static resources

        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-publicamundi-vector')
        
        return

    # IConfigurable
    
    def configure(self, config):
        
        # Setup vectorstorer module
        
        gdal_folder = config.get(
            'ckanext.publicamundi.vectorstorer.gdal_folder')

        temp_folder = config.get(
            'ckanext.publicamundi.vectorstorer.temp_dir')
        
        vectorstorer.setup(gdal_folder, temp_folder)

        return

    # IDomainObjectModification

    def notify(self, entity, operation=None):

        if isinstance(entity, model.resource.Resource):
            if entity.format.lower() in vectorstorer.supported_formats:
                # Yes, we are interested in this format
                log.info('Notified on modification %r of vector resource %r (state=%s)' % (
                    operation, entity.id, entity.state))
                if operation == model.domain_object.DomainObjectOperation.new:
                    # A new vector resource has been created
                    resource_actions.identify_resource(entity)
                elif operation == model.domain_object.DomainObjectOperation.deleted:
                    # A vector resource has been deleted
                    #resource_actions.delete_ingest_resource(entity.as_dict())
                    pass
                elif operation is None:
                    # The URL of a vector resource has been updated
                    #resource_actions.update_ingest_resource(entity)
                    pass
        elif isinstance(entity, model.Package):
            log.info('Notified on modification %r of dataset %r (state=%r)' % (
                operation, entity.id, entity.state))
            if entity.state == 'deleted':
                resource_actions.delete_ingest_resources_in_package(
                    entity.as_dict())
        return
