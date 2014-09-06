import logging
import zope.interface
import zope.schema
import zope.schema.interfaces

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.metadata import \
    dataset_types, Object, ErrorDict, \
    serializer_for_object, serializer_for_field, serializer_for_key_tuple

_t = toolkit._

def is_dataset_type(value, context):
    if not value in dataset_types:
        raise Invalid('Unknown dataset-type (%s)' %(value))
    return value

def dataset_postprocess_read(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for reading')
    # Prepare computed fields, reorganize structure etc.
    data[('baz_view',)] = u'I am a read-only Baz'
    #raise Exception('Break (postprocess read)')
    pass

def dataset_postprocess_edit(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for editing')
    #raise Exception('Break (postprocess edit)')
    
    # Todo
    # Prepare field values for storage (??)

    pass

def dataset_validate(key, data, errors, context):
    assert key[0] == '__after', 'This validator can only be invoked in the __after stage'
    logger.debug('Validating dataset for editing')
    #raise Exception('Break (validate)')
    
    # Todo 
    # - Instantiate an object (IObject provider) from flattened fields
    # - Validate at object-level

    pass

def dataset_preprocess_edit(key, data, errors, context):
    assert key[0] == '__before', 'This validator can only be invoked in the __before stage'
    logger.debug('Pre-processing dataset for editing')
    #raise Exception('Break')
    pass

def get_field_validator(field):
    '''Get field-level validation wrapped as a CKAN validator function.
    '''

    def validate(value, context):
        try: 
            # Invoke the zope.schema validator
            field.validate(value)
        except zope.schema.ValidationError as ex:
            # Map this exception to the one expected by CKAN's validator
            raise Invalid(u'Invalid data (%s)' %(type(ex).__name__))
        return value

    return validate

def get_field_input_converter(field):
    '''Get field-level input conversion wrapped as a CKAN converter function.
    
    This wrapper is intended to be used for a create/update schema converter,
    i.e. to convert input from a web request.
    '''

    def convert(value, context):
        '''Initialize or convert a field's value from the received input.
        '''

        if value is missing:
            # Do not handle missing inputs here
            return value

        if not value:
            # Determine default value and initialize   
            if field.default is not None:
                value = field.default
            elif field.defaultFactory is not None:
                value = field.defaultFactory()
        else:
            # Convert (if needed) from textual input
            if isinstance(value, basestring):
                ser = serializer_for_field(field)
                value = ser.loads(value)

        return value

    return convert

def get_field_output_converter(field):
    '''Get field-level output conversion wrapped as a CKAN converter function.

    This wrapper is intended to be used for a read schema converter, i.e. to
    convert values from db storage.
    '''

    def convert(value, context):

        assert not value is missing
        
        # Todo 

        return value

    return convert

