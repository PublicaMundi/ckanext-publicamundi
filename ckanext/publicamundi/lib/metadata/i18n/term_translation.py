'''Perform term-based translation on a certain text domain (or globally).

This is a gettext-like interface. The basic difference is that translations are
dynamic (i.e. not discovered at compile-time from source code).
'''
import zope.interface
import sqlalchemy
import sqlalchemy.orm as orm
import logging

import ckan.model as model

from ckanext.publicamundi.lib.metadata.fields import Field, IField
from ckanext.publicamundi.lib.metadata.base import FieldContext, IFieldContext
from ckanext.publicamundi.lib.languages import check as check_language

from .ibase import IFieldTranslation, IValueBasedFieldTranslation

__all__ = []

log1 = logging.getLogger(__name__)

@zope.interface.implementer(IValueBasedFieldTranslation)
class FieldTranslation(object):
    '''Provide term-based translation for fields inside a (user-defined) text domain.

    Use main database as a persistence layer.
    '''

    def __init__(self, text_domain=None):
        self._text_domain = str(text_domain)

    def __str__(self):
        return '<FieldTranslation ns=%s>' % (self.namespace)
    
    @classmethod
    def _key(cls, field):
        '''Return a string regarded as a key for a (bound) field.
        '''
        return str(field.context.value)

    ## IFieldTranslation interface ##
    
    @property
    def source_language(self):
        # Assume source messages are always in 'en' locale (as gettext does)
        return 'en'
    
    @property
    def namespace(self):
        return 'text-domain:%s' % (self._text_domain or '<global>')
  
    def get(self, field, language, state='active'):
        '''Return a translation for the given pair (field, language).
        '''
        assert isinstance(field, Field)
        verifyObject(IFieldContext, field.context)
        
        key = type(self)._key(field)
        language = check_language(language)
        
        # Todo: Lookup for this term
        
        raise NotImplementedError('Todo')

    def translate(self, field, language, value, state='active'):
        '''Add or update translation for a given pair (field, language).
        '''
        assert isinstance(field, Field)
        verifyObject(IFieldContext, field.context)
        
        key = type(self)._key(field)
        language = check_language(language)
        
        value = unicode(value)
        if not value:
            raise ValueError('value: Missing')
        
        # Todo: Add/Update this term
        
        raise NotImplementedError('Todo')

    def discard(self, field=None, language=None):
        '''Discard existing translations.
        '''
        
        if field:
            assert isinstance(field, Field)
            verifyObject(IFieldContext, field.context)
            key = type(self)._key(field)
        
        if language:
            language = check_language(language)

        # Todo
        
        raise NotImplementedError('Todo')
 
    ## IValueBasedFieldTranslation interface ##

    @property
    def text_domain(self):
        return self._text_domain

