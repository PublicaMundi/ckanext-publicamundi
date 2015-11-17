'''Perform package-scoped, key-based translation for fields.
'''

import zope.interface
from zope.interface.verify import verifyObject
import sqlalchemy
import sqlalchemy.orm as orm
import logging
import pylons

import ckan.model as model

import ckanext.publicamundi.model as ext_model
from ckanext.publicamundi.lib.util import check_uuid
from ckanext.publicamundi.lib.metadata.fields import Field, IField
from ckanext.publicamundi.lib.metadata.base import FieldContext, IFieldContext

from . import language_codes, check_language
from .ibase import (IFieldTranslator, IKeyBasedFieldTranslator)

__all__ = []

log1 = logging.getLogger(__name__)

class FieldTranslator(object):
    '''Provide a key-based field translation mechanism in the scope of a package.

    Use main database as persistence layer.
    '''

    zope.interface.implements(IKeyBasedFieldTranslator)
    
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
            source_language = pylons.config['ckan.locale_default']
            log1.info('package %s: source-language is missing and cannot be deduced' % (
                package_id))
        if not source_language in language_codes:
            raise ValueError(
                'source_language: Expected an iso-639-1 language code')
        self._source_language = source_language
        
        self._defer_commit = False

    def __str__(self):
        return '<FieldTranslator ns=%s source=%s>' % (
            self.namespace, self.source_language)
    
    @classmethod
    def _key(cls, field):
        '''Return a string regarded as a key for a (bound) field.
        '''

        key = field.context.key
        if isinstance(key, tuple):
            key = '.'.join(map(str, key))
        else:
            key = str(key)
        
        if not key:
            raise ValueError('field: Expected non-empty key path at context.key')
        return key
    
    ## IFieldTranslator interface ## 
    
    @property
    def source_language(self):
        return self._source_language

    @property
    def namespace(self):
        return 'package:%s' % (self._package_id)
    
    def get(self, field, language, state='active'):
        '''Return a translation for the given pair (field, language).
        '''
        assert isinstance(field, Field)
        verifyObject(IFieldContext, field.context)

        key = type(self)._key(field)
        language = check_language(language)

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
        
        if value:
            return field.bind(FieldContext(key=field.context.key, value=value))
        return None

    def translate(self, field, value, language, state='active'):
        '''Add or update translation for a given pair (field, language).
        '''
        assert isinstance(field, Field)
        verifyObject(IFieldContext, field.context)
        
        key = type(self)._key(field)
        language = check_language(language)

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

    def discard(self, field=None, language=None):
        '''Discard existing translations.
        '''
        
        cond = dict(
            package_id = self._package_id,
            source_language = self._source_language,
        )

        if field:
            assert isinstance(field, Field)
            verifyObject(IFieldContext, field.context)
            key = type(self)._key(field)
            cond['key'] = key
        
        if language:
            language = check_language(language)
            cond['language'] = str(language)
        
        q = model.Session.query(ext_model.PackageTranslation).filter_by(**cond)
        n = q.delete()

        if not self._defer_commit:
            model.Session.commit()
        return n

    ## IKeyBasedFieldTranslator interface ##

    @property
    def package_id(self):
        return self._package_id
 
