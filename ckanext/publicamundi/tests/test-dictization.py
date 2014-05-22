import json
import ckanext.publicamundi.lib.dictization as dictization

d = {
    'foo': {
        'a': 99,
        'b': {
            'b1': 'B1',
            'b2': 'B2',
        },
    },
    'measurements': {
        'created': '12-Dec-2014',
        'samples': {
            'a': [ 1.4 ,7.6, 9.7, 5.9, 5.0, 9.1, 11.3, ],
            'b': [ 4.9 ],
            'c': [],
        },
    },
    'author': u'lalakis',
}

d1 = dictization.flatten(d)

for k in sorted(d1):
    print k, ': ', d1[k]

d2 = dictization.unflatten(d1)
print json.dumps(d2, indent=4)

