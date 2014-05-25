import logging
import zope.interface
import zope.schema

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.publicamundi.lib.metadata import dataset_types

_t = toolkit._

log1 = logging.getLogger(__name__)

def is_dataset_type(value, context):
    if not value in dataset_types:
        raise Invalid('Unknown dataset_type (%s)' %(value))

def dataset_postprocess_read(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    log1.debug('Post-processing dataset for reading')
    # Prepare computed fields, reorganize structure etc.
    data[('baz_view',)] = u'I am a read-only Baz'
    #raise Exception('Break (postprocess read)')
    pass

def dataset_postprocess_edit(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    log1.debug('Post-processing dataset for editing')
    #raise Exception('Break (postprocess edit)')
    pass

def dataset_validate(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    log1.debug('Validating dataset for editing')
    #raise Exception('Break (validate)')
    pass

def dataset_preprocess_edit(key, data, errors, context):
    assert key[0] == '__before', 'This validator can only be invoked in the __before stage'
    log1.debug('Pre-processing dataset for editing')
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

