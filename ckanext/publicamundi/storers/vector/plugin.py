from pylons import config

import ckan.plugins as p
from ckan import model
from ckan.lib.dictization.model_dictize import resource_dictize

from ckanext.publicamundi.storers.vector import settings, resource_actions
from ckanext.publicamundi.storers.vector.lib import actions


class VectorStorer(p.SingletonPlugin):
    STATE_DELETED = 'deleted'

    resource_delete_action = None
    resource_update_action = None

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IResourceUrlChange)
    p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.IActions, inherit=True)

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
            '/api/search_epsg',
            controller=exportController,
            action='search_epsg')

        map.connect(
            'vector_ingest',
            '/api/vector/ingest/{resource_id}',
            controller=vectorController,
            action='ingest',
            resource_id='{resource_id}')

        return map

    def get_actions(self):
        return {
            'resource_update': actions.new_resource_update,
            'resource_delete': actions.new_resource_delete,
        }

    def update_config(self, config):

        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-vectorstorer')

    def notify(self, entity, operation=None):

        if isinstance(entity, model.resource.Resource):

            if (operation == model.domain_object.DomainObjectOperation.new and
               entity.format.lower() in settings.VECTOR_FORMATS):
                # A new vector resource has been created

                resource_actions.identify_resource(entity)
            # elif (operation == model.domain_object.
            # DomainObjectOperation.deleted):
                # A vectorstorer resource has been deleted
                # resource_actions.delete_vector_storer_task(entity.as_dict())

            # elif operation is None:
                # Resource Url has changed

                # if entity.format.lower() in settings.SUPPORTED_DATA_FORMATS:
                # Vector file was updated

                # resource_actions.update_vector_storer_task(entity)

        # else :
            # Resource File updated but not in supported formats

            # resource_actions.delete_vector_storer_task(entity.as_dict())

        elif isinstance(entity, model.Package):

            if entity.state == self.STATE_DELETED:

                resource_actions.pkg_delete_vector_storer_task(
                    entity.as_dict())
