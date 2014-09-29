import re
import json
import autopep8
import datadiff.tools
import dictdiffer

def assert_faulty_keys(x, expected_keys=[], expected_invariants=[]):
    '''Verify that a set of fields (given with their keys) fail to validate'''

    expected_keys = set(expected_keys)

    errs_dict = x.validate(dictize_errors=True)

    faulty_keys = set(errs_dict.keys())

    print ' ** Errors:\n%s' %(json.dumps(errs_dict, indent=4))
    print ' ** Keys not expected but failed: %s' %(faulty_keys - expected_keys)
    print ' ** Keys expected but not failed: %s' %(expected_keys - faulty_keys)

    if not expected_keys:
        assert not errs_dict
    else:
        assert errs_dict
        assert expected_keys == faulty_keys
        if '__after' in errs_dict.keys():
            print ' ** Expected invariants (to fail):', expected_invariants
            print ' ** Failed invariants:', json.dumps(errs_dict['__after'])
            for k in expected_invariants:
                print ' ** Matching error string for', k
                assert re.search(k, json.dumps(errs_dict['__after']))

def assert_equal(d1, d2):
    datadiff.tools.assert_equal(d1, d2)

def diff_dicts(d1, d2):
    return list(dictdiffer.diff(d1, d2))

def patch_dict(diff_result, d):
    dictdiffer.patch(diff_result, d)

def pprint_code(s):
    return autopep8.fix_code(s, options=autopep8.parse_args(['-a', '']))


