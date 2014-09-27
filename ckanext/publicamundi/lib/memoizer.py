
# Note Not sure if _cache is thread-safe. It is supposed to be as of GIL, see:
# https://docs.python.org/2/glossary.html#term-global-interpreter-lock
# If not, it should be replaced by a threading.local instance.
_cache = dict()

def memoize(fn):
    #print 'Creating memoize wrapper for %r ...' %(fn)
    cached_results = _cache[fn] = dict()
    def wrapped(*args):
        cid = args
        if cid in cached_results:
            res = cached_results[cid]
        else:
            res = cached_results[cid] = fn(*args)
        return res
    return wrapped

