import json
import re

from ckanext.publicamundi import reference_data

_datafile = reference_data.get_path('language-codes-3b2.json')
_data = None
with open(_datafile, 'r') as fp:
    _data = json.loads(fp.read())

_re_alpha2 = re.compile('^[a-z]{2,2}$')
_re_alpha3b = re.compile('^[a-z]{3,3}$')

def get_all(table='iso-639-1'):
    '''Return a dict of languages as coded in the given standardization (table).

    Allowed values for parameter `table` are:
     * iso-639-1 
     * alpha-2 (synonym to iso-639-1)
     * iso-639-2
     * alpha-3, alpha-3b (synonym to iso-639-2)
    '''

    key = None
    if table in ['iso-639-2', 'alpha-3', 'alpha-3b']:
        key = 'alpha3b'
    elif table in ['iso-639-1', 'alpha-2']:
        key = 'alpha2'
    else:
        raise ValueError('Unknown code table: %s' % (table))
    
    return {r[key]: r['name_en'] for r in _data}

def get_by_code(code, table=None):
    '''Search the name of a language by iso-639-[12] code
    '''
    
    key = None
    if not table:
        if _re_alpha2.match(code):
            key = 'alpha2'
        elif _re_alpha3b.match(code):
            key = 'alpha3b'
        else:
            raise ValueError('Unexpected language code: %s' % (code))
    else:
        if table == 'iso-639-1':
            key = 'alpha2' 
        elif table == 'iso-639-2':
            key = 'alpha3b'
        else:
            raise ValueError('Unexpected language code table: %s' % (table))
            
    res = None
    try: 
        i = map(lambda r: r[key], _data).index(code)
    except:
        pass
    else:
        res = _data[i]    
    return res

by_code = get_by_code

def check(code, table='iso-639-1'):
    if not code:
        raise ValueError('Missing or empty')
    if not get_by_code(code, table):
        raise ValueError('Unknown language code for %s: %r' % (table, code))
    return code

