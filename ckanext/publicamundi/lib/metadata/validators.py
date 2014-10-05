import logging
import zope.interface
import zope.schema
import zope.schema.interfaces
import itertools
from collections import Counter

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib.util import Breakpoint
from ckanext.publicamundi.lib.util import find_all_duplicates
from ckanext.publicamundi.lib.metadata import (
    dataset_types, Object, ErrorDict,
    serializer_for_object, serializer_for_field, serializer_for_key_tuple)

_t = toolkit._

## Helpers

def objectify(factory, data, key_prefix):
    '''Build an object from received converter/validator data. 
    '''

    prefix = key_prefix + '.'
    
    def is_field_key(k):
        if not k or len(k) > 1:
            return False
        return k[0].startswith(prefix)
    
    obj = None
    obj_dict = { k[0]: data[k] for k in data if is_field_key(k) }
    if obj_dict:
        obj = factory().from_dict(obj_dict, is_flat=True, opts={
            'unserialize-keys': True, 
            'key-prefix': key_prefix, 
            'unserialize-values': 'default', 
        })

    assert not obj or isinstance(obj, Object)
    return obj

def dictize_for_extras(obj, key_prefix):
    '''Dictize an object in proper way so that it's fields can be stored 
    under package_extra KV pairs.
    '''

    assert isinstance(obj, Object)
    
    dictz_opts = {
        'serialize-keys': True, 
        'serialize-values': 'default',
        'key-prefix': key_prefix,
    }
    res = obj.to_dict(flat=True, opts=dictz_opts)
    res = { k: v for k, v in res.iteritems() if v is not None }
    return res

## Validators/Converters 

def is_dataset_type(value, context):
    if not value in dataset_types:
        raise Invalid('Unknown dataset-type (%s)' %(value))
    return value

def preprocess_dataset_for_read(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    
    def debug(msg):
        logger.debug('Pre-processing dataset for reading: %s' %(msg))
    
    debug('context=%r' %(context.keys()))
    
    #raise Breakpoint('preprocess read')
    pass

def postprocess_dataset_for_read(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
    
    def debug(msg):
        logger.debug('Post-processing dataset for reading: %s' %(msg))
    
    debug('context=%r' %(context.keys()))
    
    # Note This is not always supplied (?). I suppose this is due to the
    # fact that package dicts are cached (on their revision-id).
    requested_with_api = context.has_key('api_version')
    
    # Prepare computed fields, reorganize structure etc.
    #data[('baz_view',)] = u'I am a read-only Baz'
    #data[('baz_view',)] = { 'a': 99, 'b': { 'measurements': [ 1, 5, 5, 12 ] } }

    #raise Breakpoint('postprocess read')
    pass

def postprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
     
    def debug(msg):
        logger.debug('Post-processing dataset for editing: %s' %(msg))
 
    debug('context=%r' %(context.keys()))
    
    requested_with_api = context.has_key('api_version')
    is_new = not context.has_key('package')
    is_draft = data.get(('state',), 'unknown').startswith('draft')

    #raise Breakpoint('postprocess_dataset_for_edit')

    if is_new and not requested_with_api:
        return # noop: only core metadata expected

    dt = data[('dataset_type',)]
    dt_spec = dataset_types.get(dt)
    if not dt_spec:
        raise Invalid('Unknown dataset-type: %s' %(dt))
    
    key_prefix = dt_spec.get('key_prefix', dt)
    
    # 1. Objectify from flattened fields
    
    obj = objectify(dt_spec.get('class'), data, key_prefix)

    if not obj:
        # Failed to create one (maybe at resources form (?))
        return 

    data[(key_prefix,)] = obj
    
    # 2. Validate as an object

    validation_errors = obj.validate(dictize_errors=True)
    # Todo Try to map `validation_errors` to `errors`
    #assert not validation_errors
   
    # 3. Convert fields to extras
    
    extras_list = data[('extras',)]
    extras_dict = dictize_for_extras(obj, key_prefix)
    for key, val in extras_dict.iteritems():
        extras_list.append({ 'key': key, 'value': val })
    assert not find_all_duplicates(map(lambda t: t['key'], extras_list))
    
    debug('Saved %d %s-related fields into extras' % (len(extras_dict), dt))
    return

def preprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    
    def debug(msg):
        logger.debug('Pre-processing dataset for editing: %s' %(msg))
    
    debug('context=%r' %(context.keys()))
    
    received_data = { k:v for k,v in data.iteritems() if not (v is missing) }
    unexpected_data = received_data.get(('__extras',), {})
    
    debug('Received data: %r' %(received_data))
    debug('Received (but unexpected) data: %r' %(unexpected_data))
    
    # Figure-out if a nested dict is supplied (instead of a flat one).
    
    # Note This "nested" input format is intended to be used by the action api,
    # as it is far more natural to the JSON format. Still, this format option is
    # not restricted to api requests (it is possible to be used even by form-based
    # requests).
    
    dt = received_data.get(('dataset_type',))
    r = unexpected_data.get(dt) if dt else None
    if isinstance(r, dict) and dataset_types.has_key(dt):
        # Looks like a nested dict keyed at key_prefix
        key_prefix = dataset_types[dt]['key_prefix']
        debug('Trying to flatten input at %s' %(key_prefix))
        if any([ k[0].startswith(key_prefix) for k in received_data ]):
            raise Invalid('Not supported: Detected both nested/flat inputs')
        # Convert to expected flat fields
        key_converter = lambda k: '.'.join((key_prefix,) +k)
        r = dictization.flatten(r, key_converter)
        data.update({ (k,): v for k, v in r.iteritems() })

    #raise Breakpoint('preprocess_dataset_for_edit')
    pass

def get_field_edit_processor(field):
    '''Get a field-level edit converter wrapped as a CKAN converter function.
    
    This wrapper is intended to be used for a create/update schema converter,
    and has to carry out the following basic tasks:
        - convert input from a web request
        - validate at field level
        - convert to a string form and store at data[key] 
    '''

    def convert(key, data, errors, context):
        value = data.get(key)
        logger.debug('Processing field %s for editing (%r)', key[0], value)
         
        ser = serializer_for_field(field)

        # Not supposed to handle missing inputs here
        
        assert not value is missing
        
        # Convert from input/db or initialize to defaults
        
        if not value:
            # Determine default value and initialize   
            if field.default is not None:
                value = field.default
            elif field.defaultFactory is not None:
                value = field.defaultFactory()
        else:
            # Convert from input or db  
            if ser and isinstance(value, basestring):
                try:
                    value = ser.loads(value)
                except Exception as ex:
                    raise Invalid(u'Invalid input (%s)' % (ex.message))
        
        # Ignore empty values (act exactly as the `ignore_empty` validator).
        # Note If a field is marked as required, the check is postponed until
        # the dataset is validated at dataset level.

        if not value:
            data.pop(key)
            raise StopOnError

        # Validate
        
        try: 
            # Invoke the zope.schema validator
            field.validate(value)
        except zope.schema.ValidationError as ex:
            # Map this exception to the one expected by CKAN
            raise Invalid(u'Invalid (%s)' % (type(ex).__name__))

        # Convert to a properly formatted string (for db storage)

        if ser:
            value = ser.dumps(value)
        
        data[key] = value

        return

    return convert

def get_field_read_processor(field):
    '''Get a field-level converter wrapped as a CKAN converter function.
    '''

    def convert(key, data, errors, context):
        value = data.get(key)
        logger.debug('Processing field %s for reading (%r)', key[0], value)
        
        assert not value is missing
        assert isinstance(value, basestring)
        
        if not value:
            logger.warn('Read empty value for field %s' % (key[0]))

        # noop

        return

    return convert

