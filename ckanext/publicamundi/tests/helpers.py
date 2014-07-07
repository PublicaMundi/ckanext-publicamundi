import nose.tools
import json

@nose.tools.nottest
def assert_faulty_keys(field,expected_keys):
    errs1 = field.validate()
    errs1_dict = field.dictize_errors(errs1)
    print json.dumps(errs1_dict, indent=4)
    if not expected_keys:
        assert not errs1_dict
        pass
    else:
        assert errs1_dict
        #assert (expected_keys.issubset(set(errs1_dict.keys())) and set(errs1_dict.keys()).issubset(expected_keys))
        assert expected_keys == set(errs1_dict.keys())


