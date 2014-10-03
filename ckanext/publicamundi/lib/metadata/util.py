'''Several metadata-related utilities (that dont fit anywhere else)
'''
import zope.interface
import zope.schema
from itertools import product, chain

from ckanext.publicamundi.lib.metadata import schemata 

def iter_object_schemata():
    '''Iterate on every (defined under .schemata) schema
    '''

    for name in dir(schemata):
        x = getattr(schemata, name)
        if not isinstance(x, zope.interface.interface.InterfaceClass):
            continue
        if not x.extends(schemata.IObject):
            continue
        yield x

def iter_field_adaptee_vectors():
    '''Iterate on every field adaptee vector that could possibly be registered 
    to  the adapter registry (until a length of 3).
    '''

    from ckanext.publicamundi.lib.metadata.fields import (
        container_ifaces, leaf_ifaces)
    
    object_ifaces = list(iter_object_schemata())

    g1 = ((r,) for r in leaf_ifaces)
    
    gf2 = product(container_ifaces, leaf_ifaces)
    gs2 = product(container_ifaces, object_ifaces)
    
    #gf3 = product(container_ifaces, container_ifaces, leaf_ifaces)
    #gs3 = product(container_ifaces, container_ifaces, object_ifaces)

    adaptee_vectors = chain(g1, gf2, gs2)

    return adaptee_vectors

