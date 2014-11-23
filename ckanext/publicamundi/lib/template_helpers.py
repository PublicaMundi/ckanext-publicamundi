import datetime

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib import resource_ingestion

def resource_ingestion_result(resource_id):
    return resource_ingestion.get_result(resource_id)

