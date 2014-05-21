import zope.interface
import zope.schema
import ckanext.publicamundi.lib.metadata as pm_metadata

X = pm_metadata.InspireMetadata

print
print ' ** Fields (flattened) for %s ** ' %(X)
print
res = X.get_flattened_fields()
for k in sorted(res):
    print k, '->', res[k]

print
print ' ** Fields for %s ** ' %(X)
print
res = X.get_fields()
for k in sorted(res):
    print k, '->', res[k]

