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
            'unserialize-values': 'json', 
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
        'serialize-values': 'json',
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
    logger.debug('Pre-processing dataset for reading: context=%r' %(
        context.keys()))
    
    #raise Breakpoint('preprocess read')
    pass

def postprocess_dataset_for_read(key, data, errors, context):
    assert key[0] == '__after', \
        'This validator can only be invoked in the __after stage'
    logger.debug('Post-processing dataset for reading: context=%r' %(
        context.keys()))
    
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
    logger.debug('Post-processing dataset for editing: context=%r' %(
        context.keys()))
    
    requested_with_api = context.has_key('api_version')

    is_new = not context.has_key('package')
    is_draft = data.get(('state',), 'unknown').startswith('draft')

    if is_new and not requested_with_api:
        return # noop: core metadata expected

    dt = data[('dataset_type',)]
    dt_spec = dataset_types[dt]
    key_prefix = dt_spec.get('key_prefix', dt)
    
    # 1. Objectify from flattened fields
    
    obj = objectify(dt_spec.get('class'), data, key_prefix)

    data[(key_prefix,)] = obj
    
    # 3. Validate as an object

    if obj:
        validation_errors = obj.validate(dictize_errors=True)
        # Fixme Try to map `validation_errors` to `errors`
        #assert not validation_errors
    else:
        assert is_draft
   
    # 4. Convert fields to extras

    def check_extras(extras_list):
        extras_keys = Counter(map(lambda t: t['key'], extras_list))
        return extras_keys.most_common(1)[0][1] < 2
    
    if obj:
        extras_list = data[('extras',)]
        extras_dict = dictize_for_extras(obj, key_prefix)
        for key, val in extras_dict.iteritems():
            extras_list.append({ 'key': key, 'value': val })
        assert check_extras(extras_list)

    return

def preprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    logger.debug('Pre-processing dataset for editing: context=%r' %(
        context.keys()))
    
    #raise Exception('Break')
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
        logger.debug('Processing field "%s" for editing' %(key[0]))
        
        value = data.get(key)

        # We are not supposed to handle missing inputs here
        assert not value is missing
        
        # Convert from input or initialize to defaults

        if not value:
            # Determine default value and initialize   
            if field.default is not None:
                value = field.default
            elif field.defaultFactory is not None:
                value = field.defaultFactory()
        else:
            # Convert from string input
            if isinstance(value, basestring):
                iser = serializer_for_field(field, fmt='input')
                if iser:
                    value = iser.loads(value)
        
        # Ignore empty values (equivalent to `ignore_empty` validator).
        # Note If a field is required the check is postponed until the dataset
        # is validated at object level.  
        
        if not value:
            raise StopOnError

        # Validate
        
        try: 
            # Invoke the zope.schema validator
            field.validate(value)
        except zope.schema.ValidationError as ex:
            # Map this exception to the one expected by CKAN
            raise Invalid(u'Invalid data (%s)' %(type(ex).__name__))

        # Convert to a proper string format

        jser = serializer_for_field(field, fmt='json')
        if jser:
            value = jser.dumps(value)
        
        data[key] = value

        return

    return convert

def get_field_read_processor(field):
    '''Get a field-level converter wrapped as a CKAN converter function.
    '''

    def convert(key, data, errors, context):
        logger.debug('Processing field "%s" for reading' %(key[0]))
        
        value = data.get(key)

        assert value and (not value is missing)
        assert isinstance(value, basestring)
        
        # noop

        return

    return convert

