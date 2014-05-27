import importlib
import inspect

def load_class(fq_name):
    mod_name,cls_name = fq_name.strip().split(':')
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, cls_name)
    if not inspect.isclass(cls):
        raise ValueError('The 1st argument "%s" is not a class' %(cls))
    return cls

def instantiate_class(fq_name, *args, **kwargs):
    cls = load_class(fq_name)
    return cls (*args, **kwargs)

