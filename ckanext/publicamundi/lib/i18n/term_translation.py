'''Perform term-based translation on a certain text domain (or globally).

This is a gettext-like interface. The basic difference is that translations are
dynamic (i.e. not discovered at compile-time from source code).
'''
import zope.interface
import sqlalchemy
import sqlalchemy.orm as orm

import ckan.model as model

from . import language_codes
from .ibase import ITranslator, ITermTranslator

class TermTranslator(object):
    '''Provide a term-based translation mechanism inside a (user-defined) text domain.

    Use main database as a persistence layer.
    '''

    zope.interface.implements(ITermTranslator)
    
    @property
    def source_language(self):
        # Assume source messages are always in 'en' locale (as Gettext does)
        return 'en'

    @property
    def text_domain(self):
        return self._text_domain
    
    def __init__(self, text_domain=None):
        self._text_domain = str(text_domain)

    def __str__(self):
        return '<%s domain=%s>' % (
            self.__class__.__name__, self.text_domain)
    
    ## ITranslator interface ##
    
    def get(self, key, language, state='active'):
        '''Return a translation for the given pair (key, language).
        '''
        # Todo
        raise NotImplementedError('Todo')

    def translate(self, key, value, language, state='active'):
        '''Add or update translation for a given pair (key, language).
        '''
        # Todo
        raise NotImplementedError('Todo')

    def discard(self, key=None, language=None):
        '''Discard existing translations.
        '''
        # Todo
        raise NotImplementedError('Todo')
 
