import json
import ckanext.publicamundi.lib.dictization as dictization

d = {
    u'foo': {
        u'a': 99,
        u'b': {
            u'b1': u'B1',
            u'b2': u'B2',
        },
    },
    u'measurements': {
        u'created': u'12-Dec-2014',
        u'samples': {
            'a': [ 1.4 ,7.6, 9.7, 5.9, 5.0, 9.1, 11.3, ],
            'b': [ 4.9 ],
            'c': { 
                # Here, unflatten() should detect a list 
                u'0': 99,
                u'1': 100,
                u'2': 199,
            },
        },
    },
    u'author': u'lalakis',
}

d1 = dictization.flatten(d)

for k in sorted(d1):
    print k, ': ', d1[k]

d2 = dictization.unflatten(d1)
print json.dumps(d2, indent=4)

