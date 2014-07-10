import nose.tools
import re
import json

@nose.tools.nottest
def assert_faulty_keys(field, expected_keys=None, expected_invariants=None):
    errs = field.validate()
    errs_dict = field.dictize_errors(errs)
    print json.dumps(errs_dict, indent=4)
    if not expected_keys:
        assert not errs_dict
        pass
    else:
        assert errs_dict
        assert expected_keys == set(errs_dict.keys())
        if '__after' in errs_dict.keys():
            #print 'expected_invariants = ', expected_invariants
            #print 'errs_dict = ', json.dumps(errs_dict['__after'])
            for k in expected_invariants:
                #print 'k = ', k
                assert re.search(k, json.dumps(errs_dict['__after']))
                #json.dumps(errs_dict['__after'])





