from functools import wraps

# Note Not sure if _cache is thread-safe. 
# At least for CPython, it is supposed to be safe as of GIL, see:
# https://docs.python.org/2/glossary.html#term-global-interpreter-lock
# If not, it should be replaced by a threading.local instance.
_cache = dict()

def memoize(fn):
    cached_results = _cache[fn] = dict()
    @wraps(fn)
    def wrapped(*args):
        cid = args
        if cid in cached_results:
            res = cached_results[cid]
        else:
            res = cached_results[cid] = fn(*args)
        return res
    return wrapped

