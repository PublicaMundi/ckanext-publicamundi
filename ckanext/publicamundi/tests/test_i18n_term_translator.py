# -*- encoding: utf-8 -*-

import zope.interface
import zope.schema
from zope.interface.verify import verifyObject, verifyClass

from nose.tools import istest, nottest, raises

from ckanext.publicamundi.lib.i18n.ibase import ITranslator, ITermTranslator
from ckanext.publicamundi.lib.i18n.term_translation import TermTranslator

def test_interface():
    
    translator = TermTranslator('publicamundi')
    assert verifyObject(ITermTranslator, translator)
    assert not zope.schema.getValidationErrors(ITermTranslator, translator)
    
    translator = TermTranslator() # global text domain
    assert verifyObject(ITermTranslator, translator)
    assert not zope.schema.getValidationErrors(ITermTranslator, translator)
    
