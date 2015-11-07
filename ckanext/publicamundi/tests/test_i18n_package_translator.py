# -*- encoding: utf-8 -*-

import zope.interface
import zope.schema
from zope.interface.verify import verifyObject, verifyClass

from nose.tools import istest, nottest, raises

from ckanext.publicamundi.lib.i18n.ibase import ITranslator, IPackageTranslator
from ckanext.publicamundi.lib.i18n.package_translation import PackageTranslator

def test_interface():
    
    translator = PackageTranslator('6b1d06b6-b1d3-4ba2-8e62-c5c410ed502a', 'el')
    assert verifyObject(IPackageTranslator, translator)
    assert not zope.schema.getValidationErrors(IPackageTranslator, translator)
     
    translator = PackageTranslator(package={
        'id': '6b1d06b6-b1d3-4ba2-8e62-c5c410ed502a',
        'language': 'el',
    })
    assert verifyObject(IPackageTranslator, translator)
    assert not zope.schema.getValidationErrors(IPackageTranslator, translator)
