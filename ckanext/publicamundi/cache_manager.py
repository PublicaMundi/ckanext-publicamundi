from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

_cache_manager = None

def setup(config):
    '''Setup module-global CacheManager'''
    global _cache_manager

    opts = parse_cache_config_options(config)
    _cache_manager = CacheManager(**opts) 

    return

def get_cache(name):
    '''Get a configured instance of Cache. 
    '''
    return _cache_manager.get_cache(name)
    
