import logging
import zope.interface
import zope.schema

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

import ckanext.publicamundi.lib
from ckanext.publicamundi.lib.metadata import dataset_types

_t = toolkit._

log1 = logging.getLogger(__name__)

def is_dataset_type(value, context):
    if not value in dataset_types:
        raise Invalid('Unknown dataset_type (%s)' %(value))

def validate_dataset(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    baz = data.get(('baz',))
    #raise Exception('Break')
    pass

def get_field_validator(field):
    def validate(value, context):
        try: 
            # Invoke the zope.schema validator
            field.validate(value)
        except zope.schema.ValidationError as ex:
            # Map this exception to the one expected by CKAN's validator
            raise Invalid(u'Invalid data (%s)' %(type(ex).__name__))
        return value
    return validate

