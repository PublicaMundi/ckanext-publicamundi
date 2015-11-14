import zope.interface
import functools
from unidecode import unidecode

from ckan.lib.munge import (munge_name, munge_title_to_name) 

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter, factory_for_object, class_for_object)
from ckanext.publicamundi.lib.metadata.schemata import *


def deduce(key0, *rkeys):
    scalar_types = (basestring, int, long, float, bool,)
    def decorate(method):
        @functools.wraps(method)
        def wrap_method(o):
            result = method(o)
            # Fix returning type
            if not len(rkeys) and not isinstance(result, dict):
                return {key0: result}
            if result is None:
                return {}
            return result
        wrap_method.deduce = (key0,) + rkeys
        return wrap_method
    return decorate

class BaseMetadata_Type(type):

    def __init__(cls, name, bases, cls_dict):
        type.__init__(cls, name, bases, cls_dict)
        cls._prepare_deducible_fields()

    def _prepare_deducible_fields(cls):
        cls._deduce_ = dict()
        is_method = lambda k, f: not k.startswith('__') and callable(f) 
        for f in (v for a, v  in vars(cls).iteritems() if is_method(a, v)):
            field_names = getattr(f, 'deduce', None)
            if field_names:
                cls._deduce_[f] = set(field_names)

class BaseMetadata(Object):
    __metaclass__ = BaseMetadata_Type    
    
    zope.interface.implements(IBaseMetadata)
    
    ## IBaseMetadata interface ##

    def deduce_fields(self, *keys):
        return self._deduce_fields(*keys, inherit=True, include_native=True)
   
    ## Implementation for deduce_fields ##
    
    def _deduce_fields(self, *keys, **opts):
        
        inherit = opts.get('inherit', False)
        include_native = opts.get('include_native', False)
        keys = set(keys) if keys else None
        
        unknown_opts = set(opts).difference({'inherit', 'include_native'})
        assert not unknown_opts, 'Encountered unknown kw arguments: ' % (unknown_opts)

        res = {} # always return a dict
        
        if include_native and keys:
            for k in keys:
                try:
                    res[k] = getattr(self, k)
                except AttributeError:
                    pass
            # No need to deduce, if already present
            keys.difference_update(res)
            # If everything was resolved via attributes, stop here
            if not keys:
                return res
        
        if not inherit:
            res1 = self._compute_deducible_fields(keys)
            res.update(res1)
        else:
            mro = type(self).mro()
            if not keys:
                for cls in reversed(mro):
                    res1 = self._compute_deducible_fields(None, cls=cls)
                    res.update(res1)
            else:
                for cls in mro:
                    res1 = self._compute_deducible_fields(keys, cls=cls)
                    res.update(res1)
                    keys.difference_update(res1)
                    if not keys:
                        break # done; no need to descend further in MRO
        
        return res
                    
    def _compute_deducible_fields(self, keys, cls=None):
        '''Compute requested (deducible) fields. 
        
        Behave as an instance of class cls.
        '''

        if not cls:
            cls = type(self)
        assert isinstance(self, cls)
        
        if not (hasattr(cls, '_deduce_') and len(cls._deduce_)):
            return {}
        
        coverf = None
        if not keys:
            # Gather all fields
            coverf = cls._deduce_.iterkeys()
        else:
            # Gather only requested fields, use cover approximation
            uncovered = set(keys)
            coverf = []
            coverage = lambda f: len(cls._deduce_[f].intersection(uncovered)) 
            while uncovered:
                f = max(cls._deduce_.iterkeys(), key=coverage)
                if coverage(f) > 0:
                    coverf.append(f)
                    uncovered.difference_update(cls._deduce_[f])
                else:
                    break # requested set cannot be fully covered
            
        # Compute
        res = {}
        for f in coverf:
            res.update(f(self))
        
        # If specific keys were requested, filter junk
        if keys:
            for k in res.keys():
                if not k in keys:
                    res.pop(k)
 
        return res

class Metadata(BaseMetadata):
    
    zope.interface.implements(IMetadata)
    
    title = None
    
    @deduce('title', 'name')
    def _deduce_name(self):
        transliterated_title = unidecode(self.title)
        return {
            'title': self.title,
            'name': munge_title_to_name(transliterated_title),
        }

def factory_for_metadata(name):
    if not name:
        raise ValueError('Expected a non-empty name for a dataset-type')
    return factory_for_object(IMetadata, name)

def class_for_metadata(name):
    if not name:
        raise ValueError('Expected a non-empty name for a dataset-type')
    return class_for_object(IMetadata, name)

# Provide the means to register a dataset-type 

def dataset_type(name):
    assert name, 'A dataset-type needs a non-empty name'
    def decorate(cls):
        assert issubclass(cls, Metadata)
        adapter_registry.register([], IMetadata, name, cls)
        cls.__dataset_type = name
        return cls 
    return decorate 

# Import types into our namespace

from ._common import *
from .thesaurus import Thesaurus, ThesaurusTerms
from .ckan_metadata import CkanMetadata
from .inspire_metadata import InspireMetadata
from .foo import FooMetadata
from .baz import BazMetadata

