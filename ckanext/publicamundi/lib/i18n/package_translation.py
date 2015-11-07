'''Perform key-based translation for field values.
'''
import zope.interface
import sqlalchemy
import sqlalchemy.orm as orm

import ckan.model as model

import ckanext.publicamundi.model as ext_model
from ckanext.publicamundi.lib.util import check_uuid

from . import language_codes
from .ibase import ITranslator, IPackageTranslator

class PackageTranslator(object):
    '''Provide a key-based translation mechanism in the scope of a package.

    Use main database as a persistence layer.
    '''

    zope.interface.implements(IPackageTranslator)

    @property
    def package_id(self):
        return self._package_id
    
    @property
    def source_language(self):
        return self._source_language

    def defer_commit(self, flag=True):
        self._defer_commit = flag

    def __init__(self, package, source_language=None):
        
        if isinstance(package, dict):
            package_id = str(package['id'])
        else:
            package_id = str(package)
        package_id = check_uuid(package_id)
        if not package_id:
            raise ValueError('package: Expected a UUID identifier')
        self._package_id = package_id
        
        if not source_language and isinstance(package, dict): 
            source_language = package.get('language')
        if not source_language:
            raise ValueError(
                'source_language: Missing, and cannot deduce it from package')
        if not source_language in language_codes:
            raise ValueError(
                'source_language: Expected an iso-639-1 language code')
        self._source_language = source_language
        
        self._defer_commit = False

    def __str__(self):
        return '<%s package=%s language=%s>' % (
            self.__class__.__name__, self.package_id, self.source_language)
    
    ## ITranslator interface ## 

    def get(self, key, language, state='active'):
        '''Return a translation for the given pair (key, language).
        '''
        
        key = '.'.join(key) if isinstance(key, (tuple, list)) else str(key)
        if not key:
            raise ValueError('key: Expected a non-empty key path')

        if not language:
            raise ValueError('language: Missing')
        if not language in language_codes:
            raise ValueError('language: Expected an iso-639-1 language code')
     
        # Lookup for a translation on this key
        
        cond = dict(
            package_id = self._package_id,
            source_language = self._source_language,
            key = key,
            language = language)
        if state and (state != '*'):
            cond['state'] = state
        r1, value = None, None
        q = model.Session.query(ext_model.PackageTranslation).filter_by(**cond)
        try:
            r1 = q.one()
        except orm.exc.NoResultFound as ex:
            pass
        else:
            value = r1.value
        
        return value

    def translate(self, key, value, language, state='active'):
        '''Add or update translation for a given pair (key, language).
        '''
        
        key = '.'.join(key) if isinstance(key, (tuple, list)) else str(key)
        if not key:
            raise ValueError('key: Expected a non-empty key path')

        if not language:
            raise ValueError('language: Missing')
        if not language in language_codes:
            raise ValueError('language: Expected an iso-639-1 language code')
       
        value = unicode(value)
        if not value:
            raise ValueError('value: Missing')
        
        # Insert or update a translation

        cond = dict(
            package_id = self._package_id,
            source_language = self._source_language,
            key = key,
            language = language)
        q = model.Session.query(ext_model.PackageTranslation).filter_by(**cond)
        r1 = None
        try:
            r1 = q.one()
        except orm.exc.NoResultFound as ex:
            # Insert
            r1 = ext_model.PackageTranslation(**cond)
            model.Session.add(r1)
        
        r1.value = value
        r1.state = state
        
        if not self._defer_commit:
            model.Session.commit()
        return

    def discard(self, key=None, language=None):
        '''Discard existing translations.
        '''
        
        cond = dict(
            package_id = self._package_id,
            source_language = self._source_language,
        )

        if key:
            key = '.'.join(key) if isinstance(key, (tuple, list)) else str(key)
            cond['key'] = key
        
        if language:
            cond['language'] = str(language)
        
        q = model.Session.query(ext_model.PackageTranslation).filter_by(**cond)
        n = q.delete()

        if not self._defer_commit:
            model.Session.commit()
        return n

