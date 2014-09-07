import logging
import zope.interface
import zope.schema
import zope.schema.interfaces
import itertools
from collections import Counter

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.util import Breakpoint
from ckanext.publicamundi.lib.metadata import \
    dataset_types, Object, ErrorDict, \
    serializer_for_object, serializer_for_field, serializer_for_key_tuple

_t = toolkit._

## Helpers

def get_field_key_predicate(prefix):
    name_prefix = prefix + '.'
    
    def check(k): 
        if not k or len(k) > 1:
            return False
        return k[0].startswith(name_prefix)
    
    return check

def objectify(factory, data, key_prefix):
    '''Build an object from received converter/validator data. 
    '''

    obj = None
    
    is_field_key = get_field_key_predicate(key_prefix)
    field_keys = filter(is_field_key, data.iterkeys())
    obj_dict = { key[0]: data[key] for key in field_keys }
    
    if obj_dict:
        dictz_opts = { 
            'unserialize-keys': True, 
            'unserialize-values': False, 
            'key-prefix': key_prefix 
        }
        obj = factory().from_dict(obj_dict, is_flat=True, opts=dictz_opts)

    assert not obj or isinstance(obj, Object)
    return obj

def dictize_for_extras(obj, key_prefix):
    '''Dictize an object in proper way so that it's fields can be stored 
    under package_extra KV pairs.
    '''

    assert isinstance(obj, Object)
    
    dictz_opts = {
        'serialize-keys': True, 
        'serialize-values': True, 
        'key-prefix': key_prefix,
    }

    res = obj.to_dict(flat=True, opts=dictz_opts)
    return res

## Validators/Converters 

def is_dataset_type(value, context):
    if not value in dataset_types:
        raise Invalid('Unknown dataset-type (%s)' %(value))
    return value

def preprocess_dataset_for_read(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    logger.debug('Pre-processing dataset for reading')
    
    #raise Breakpoint('preprocess read')
    pass

def postprocess_dataset_for_read(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for reading')
    
    # Prepare computed fields, reorganize structure etc.
    data[('baz_view',)] = u'I am a read-only Baz'
    
    #raise Breakpoint('postprocess read')
    pass

def postprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for editing')
        
    is_new = not context.has_key('package')
    is_draft = data.get(('state',), 'unknown').startswith('draft')
     
    if is_new:
        return # nop: core metadata expected

    dt = data[('dataset_type',)]
    dt_spec = dataset_types[dt]
    key_prefix = dt_spec.get('key_prefix', dt)
    
    # 1. Objectify from flattened fields
    
    obj = objectify(dt_spec.get('class'), data, key_prefix)

    data[(key_prefix,)] = obj
    
    # 3. Validate as an object

    if obj:
        validation_errors = obj.validate(dictize_errors=True)
        # Todo Try to map `validation_errors` to `errors`
        #assert not validation_errors
    else:
        assert is_draft
   
    # 4. Convert fields to extras

    def check_extras(extras_list):
        extras_keys = Counter(map(lambda t: t['key'], extras_list))
        return extras_keys.most_common(1)[0][1] < 2
    
    if obj:
        extras_list = data[('extras',)]
        extra_fields = dictize_for_extras(obj, key_prefix)
        for key, val in extra_fields.iteritems():
            extras_list.append({ 'key': key, 'value': val })
        assert check_extras(extras_list)

    return
   
def validate_dataset(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for editing: validate dataset')
    
    is_new = not context.has_key('package')
    is_draft = data.get(('state',), 'unknown').startswith('draft')
    
    dt = data[('dataset_type',)]
    dt_spec = dataset_types[dt]
    key_prefix = dt_spec.get('key_prefix', dt)
    
               
    pass

def preprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
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
                # Note Do we need a specialized input_serializer_for_field ??
                # Input from web requests does not necessarily have to be serialized
                # in the same way as for dictization.
                ser = serializer_for_field(field)
                value = ser.loads(value)

        return value

    return convert

def get_field_from_extras_converter(field):
    '''Get field-level output conversion wrapped as a CKAN converter function.

    This wrapper is intended to be used for a read schema converter, i.e. to
    convert values from package_extra to fields.
    '''

    def convert(value, context):

        assert value and not value is missing
        assert isinstance(value, basestring)

        ser = serializer_for_field(field)
        value = ser.loads(value)
         
        return value

    return convert

