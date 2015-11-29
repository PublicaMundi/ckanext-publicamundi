import json
import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary

from ckanext.publicamundi import reference_data

_datafile = reference_data.get_path('language-codes-3b2.json')
_data = None

with open(_datafile, 'r') as fp:
    _data = json.load(fp)
fp.close()
del fp

_re_alpha2 = re.compile('^[a-z]{2,2}$')
_re_alpha3b = re.compile('^[a-z]{3,3}$')

class ILanguage(zope.interface.Interface):

    code = zope.schema.NativeStringLine(required=True)
    
    table = zope.schema.Choice(
        required = True,
        vocabulary = SimpleVocabulary.fromValues(('iso-639-1', 'iso-639-2')))

    name = zope.schema.TextLine(required=True)

@zope.interface.implementer(ILanguage)
class Language(object):

    def __init__(self, code):
        global _data
        
        code = str(code)
        if not code:
            raise ValueError('The code is missing (or empty)')
        
        key, table = None, None
        if _re_alpha2.match(code):
            key, table = 'alpha2', 'iso-639-1'
        elif _re_alpha3b.match(code):
            key, table = 'alpha3b', 'iso-639-2'
        else:
            raise ValueError('Unexpected language code: %s' % (code))
     
        res = None
        try: 
            i = map(lambda r: r[key], _data).index(code)
        except:
            raise ValueError('Unknown language code for table %s' % (table))
        else:
            res = _data[i]    
       
        self.table, self.code, self.name = table, code, res['name_en'] 
        self.alpha2, self.alpha3b = res['alpha2'], res['alpha3b']
        return
    
    def __repr__(self):
        return '<Language "%s">' % (self.code)
    
    @staticmethod
    def get_all(table='iso-639-1'):
        '''Return a dict of languages as coded in the given standardization (table).

        Allowed values for parameter `table` are:
         * iso-639-1 
         * alpha-2 (synonym to iso-639-1)
         * iso-639-2
         * alpha-3, alpha-3b (synonym to iso-639-2)
        '''
        global _data

        key = None
        if table in ['iso-639-2', 'alpha-3', 'alpha-3b']:
            key = 'alpha3b'
        elif table in ['iso-639-1', 'alpha-2']:
            key = 'alpha2'
        else:
            raise ValueError('Unknown code table: %s' % (table))
    
        return {r[key]: r['name_en'] for r in _data}

def check(code):
    return Language(code).code

def by_code(code):
    '''Search the name of a language by iso-639-[12] code'''
    return Language(code)

def get_all(table='iso-639-1'):
    return Language.get_all(table)

