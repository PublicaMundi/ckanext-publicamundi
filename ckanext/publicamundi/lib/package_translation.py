'''Perform key-based translation for field values.
'''

import uuid
import sqlalchemy
import sqlalchemy.orm as orm
import pylons

import ckan.model as model

import ckanext.publicamundi.model as ext_model

PackageTranslation = ext_model.package_translation.PackageTranslation

language_codes = ext_model.package_translation.language_codes
translation_states = ext_model.package_translation.translation_states

def get_translated_field(pkg, key, language, source_language=None, state='active'):
    
    condition = dict()

    pkg_id = None
    if isinstance(pkg, dict):
        pkg_id = pkg['id']
    try:
        pkg_id = str(uuid.UUID(pkg_id))
    except:
        raise ValueError('pkg: Expected a UUID identifier')
    condition['package'] = pkg_id

    # Serialize key as a key path
    if isinstance(key, (tuple, list)):
        key = '.'.join(key)
    else:
        key = str(key)
    if not key:
        raise ValueError('key: Expected a non-empty key path')
    condition['key'] = key

    if source_language:
        if not source_language in language_codes:
            raise ValueError('source_language: Expected an iso-639-1 language code')
    elif isinstance(pkg, dict) and pkg.get('language'):
        source_language = pkg['language']
    else:
        source_language = pylons.config['ckan.locale_default']
    condition['source_language'] = source_language

    if not language in language_codes:
        raise ValueError('language: Expected an iso-639-1 language code')
    condition['language'] = language

    if not state in translation_states:
        raise ValueError('state: Not a valid state from %r' % (translation_states))
    condition['state'] = state

    # Lookup for a translation on this key

    r1, value = None, None
    q = model.Session.query(PackageTranslation).filter_by(**condition)
    try:
        r1 = q.one()
    except orm.exc.NoResultFound as ex:
        pass
    else:
        value = r1.value

    return value

def translate_field(pkg, key, language, value, source_language=None, state='active'):
    # Todo
    pass
