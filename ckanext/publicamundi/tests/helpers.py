import nose.tools
import json

@nose.tools.nottest
def test(x,expected_keys):
    '''Find schema validation errors 1'''
    errs1 = x.validate()
    errs1_dict = x.dictize_errors(errs1)
    print json.dumps(errs1_dict, indent=4)
    if not expected_keys:
        assert not errs1_dict
        pass
    else:
        assert errs1_dict
        assert (expected_keys.issubset(set(errs1_dict.keys())) and set(errs1_dict.keys()).issubset(expected_keys))


