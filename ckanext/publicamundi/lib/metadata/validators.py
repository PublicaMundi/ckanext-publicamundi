import logging
import zope.interface
import zope.schema
import zope.schema.interfaces
import itertools
from collections import Counter
from operator import attrgetter, itemgetter

import pylons
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib import dictization
import ckanext.publicamundi.lib.metadata as ext_metadata

_ = toolkit._
aslist = toolkit.aslist
asbool = toolkit.asbool


#
# Validators/Converters for package
#

def is_dataset_type(value, context):
    if not value in ext_metadata.dataset_types:
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
    assert key[0] == '__after', (
        'This validator can only be invoked in the __after stage')
    
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
    assert key[0] == '__after', (
        'This validator can only be invoked in the __after stage')
     
    def debug(msg):
        logger.debug('Post-processing dataset for editing: %s' %(msg))
    
    # The state we are moving to
    state = data.get(('state',), '') 
    
    # The previous state (if exists)
    pkg = context.get('package')
    prev_state = pkg.state if pkg else ''

    requested_with_api = 'api_version' in context
    is_new = not pkg

    if is_new and not requested_with_api:
        return # only core metadata are expected

    key_prefix = dtype = data[('dataset_type',)]
    if not dtype in ext_metadata.dataset_types:
        raise Invalid('Unknown dataset-type: %s' %(dtype))
    
    # 1. Build metadata object

    cls = ext_metadata.class_for_metadata(dtype)
    md = cls.from_converted_data(data, for_edit=True)

    if not md:
        return # failed to create (in resources form ?)

    data[(key_prefix,)] = md
    
    # 2. Validate as an object

    if not 'skip_validation' in context:
        validation_errors = md.validate(dictize_errors=True)
        # Fixme Map validation_errors to errors
        #assert not validation_errors
   
    # 3. Convert fields to extras
    
    extras_list = data[('extras',)]
    extras_list.extend(({'key': k, 'value': v} for k, v in md.to_extras()))
    
    # 4. Compute next state
    
    if 'skip_validation' in context:
        state = data[('state',)] = 'invalid' 
        #data[('private',)] = True
    
    if not state:
        if prev_state == 'invalid':
            state = data[('state',)] = 'active'
    
    return

def preprocess_dataset_for_edit(key, data, errors, context):
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    
    def debug(msg):
        logger.debug('Pre-processing dataset for editing: %s' %(msg))
    
    received_data = { k:v for k,v in data.iteritems() if not (v is missing) }
    unexpected_data = received_data.get(('__extras',), {})
    
    #debug('Received data: %r' %(received_data))
    #debug('Received (but unexpected) data: %r' %(unexpected_data))
    
    # Figure out if a nested dict is supplied (instead of a flat one).
    
    # Note This "nested" input format is intended to be used by the action api,
    # as it is far more natural to the JSON format. Still, this format option is
    # not restricted to api requests (it is possible to be used even by form-based
    # requests).
    
    key_prefix = dtype = received_data.get(('dataset_type',))
    r = unexpected_data.get(dtype) if dtype else None
    if isinstance(r, dict) and (dtype in ext_metadata.dataset_types):
        # Looks like a nested dict keyed at key_prefix
        debug('Trying to flatten input at %s' %(key_prefix))
        if any([ k[0].startswith(key_prefix) for k in received_data ]):
            raise Invalid('Not supported: Found both nested/flat dicts')
        # Convert to expected flat fields
        key_converter = lambda k: '.'.join([key_prefix] + map(str, k))
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
        #logger.debug('Processing field %s for editing (%r)', key[0], value)
         
        ser = ext_metadata.serializer_for_field(field)

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
                
        if not 'skip_validation' in context:
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
        #logger.debug('Processing field %s for reading (%r)', key[0], value)
        
        assert not value is missing
        assert isinstance(value, basestring)
        
        if not value:
            logger.warn('Read empty value for field %s' % (key[0]))

        # noop

        return

    return convert

def guess_language(key, data, errors, context):
    assert key[0] == '__after', (
        'This converter can only be invoked in the __after stage')
    
    lang = None
    extras_list = data[('extras',)]
   
    # Check if language present in extras
    
    lang_item = None
    try:
        i = map(itemgetter('key'), extras_list).index('language')
    except:
        pass
    else:
        lang_item = extras_list[i]
    
    # Try to deduce from metadata
    # Note At 1st stage of create form, md will be not available
    key_prefix = dtype = data[('dataset_type',)]
    md = data.get((key_prefix,))
    if md:
        lang = md.deduce_fields('language').get('language')
        
    # If not deduced and not present, guess is active language
    if not lang and not lang_item:
        req_lang = pylons.i18n.get_lang()
        lang = req_lang[0] if req_lang else 'en'
    
    # Create/Update extras item with our guessed value
    if lang:
        if not lang_item:
            extras_list.append({'key': 'language', 'value': lang})
        else:
            lang_item['value'] = lang
    else:
        assert lang_item
    return

#
# Validators/Converters for resources
#

def guess_resource_type_if_empty(key, data, errors, context):
    '''Guess the resource-type from the the rest of the resource dict.
    
    Try to guess the resource-type from the format (which should be always
    present and non-empty). We shall not assume that the format is converted
    to its canonical form since we dont know the order at which these field
    validators will run.
    '''
    
    value = data[key]
    if value:
        return 
    
    key0, pos, key2 = key
    assert key0 == 'resources' and key2 == 'resource_type'
    
    resource_format = data[('resources', pos, 'format')]
    resource_format = resource_format.encode('ascii').lower()
    
    api_formats = aslist(
        pylons.config.get('ckanext.publicamundi.api_resource_formats'))
    if resource_format in api_formats:
        value = 'api'
    else:
        value = 'file'

    data[key] = value
    return

#
# Helpers
#

def _must_validate(context, data):
    '''Indicate whether an object (or a particular field of it) should be validated
    under the given context.
    '''
    return not (
        ('skip_validation' in context) or 
        (data.get(('state',), '') == 'invalid'))

