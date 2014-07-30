import json
import copy
from nose.tools import raises, ok_, eq_

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

d2 = dictization.unflatten(d1)

def test_flattened_1():
    for k in sorted(d1):
        v = d1.get(k)
        assert isinstance(v, basestring) or isinstance(v, float) or isinstance(v, int), \
            '%r is not scalar' %(v)

@raises(AssertionError)
def test_inversed_1():
    s0 = json.dumps(d)
    s2 = json.dumps(d2)
    # Should fail because d[u'measurements'][u'samples']['c'] is converted to a list
    eq_(s0, s2)

def test_inversed_2():
    y0  = copy.deepcopy(d)
    y2 = copy.deepcopy(d2)
    y0[u'measurements'][u'samples'].pop('c')
    y2[u'measurements'][u'samples'].pop('c')
    s0 = json.dumps(y0)
    s2 = json.dumps(y2)
    eq_(s0, s2)

if __name__ == '__main__':

    print
    print ' == Flattened  == '
    for k in sorted(d1):
        print k, ': ', d1[k]
    print

    print ' == Unflattened == '
    print json.dumps(d2, indent=4)
    print
