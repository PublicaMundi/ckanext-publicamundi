import urlparse

from ckan.lib.base import BaseController,  c, request, abort
from ckan.logic import model
import ckan.plugins.toolkit as toolkit
import ckan
from ckanext.publicamundi.storers.raster import resource_actions

_ = toolkit._
_check_access = toolkit.check_access
_get_action = toolkit.get_action

class RasterImportController(BaseController):
    """
    Controller for interacting with WCST through ckan
    Two methods are expose:
    /api/raster/publish/{resource_id} - inserting the raster into rasdaman through WCST
    /api/raster/delete/{resource_id} - deleting the raster from rasdaman through WCST
    """

    def _make_default_context(self):
        """
        Creates a default context
        :return: the default context
        """
        return {
            'model': model,
            'session': model.Session,
            'user': c.user,
            }

    def publish(self, resource_id):
        """
        Publishes a raster resource in WCST

        :param resource_id: String the id of the resource
        """
        context = self._make_default_context()
        try:
            _check_access('resource_update', context, dict(id=resource_id))
        except toolkit.ObjectNotFound as ex:
            abort(404)
        except toolkit.NotAuthorized as ex:
            abort(403, _('Not authorized to update resource'))
        resource = model.Session.query(model.Resource).get(resource_id)
        resource_actions.create_ingest_resource_task(resource)

    def delete(self, resource_id):
        """
        Deletes the raster resource using WCST

        :param resource_id: String the id of the resource
        """
        context = self._make_default_context()
        try:
            _check_access('resource_update', context, dict(id=resource_id))
        except toolkit.ObjectNotFound as ex:
            abort(404)
        except toolkit.NotAuthorized as ex:
            abort(403, _('Not authorized to update resource'))
        resource = model.Session.query(model.Resource).get(resource_id)
        resource_actions.create_delete_resource_task(resource)

    def finalize(self, resource_id):
        """
        Finalizes the ingestion process and marks the resource as published

        :param resource_id: String the id of the resource
        """
        resource = model.Session.query(model.Resource).get(resource_id)
        resource_actions.change_resource_to_published(resource)