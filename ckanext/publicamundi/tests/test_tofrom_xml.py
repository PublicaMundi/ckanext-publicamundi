import zope.interface
import zope.schema
import copy
import json
import datetime
import nose.tools

from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import ThesaurusTerms, Thesaurus
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import InspireMetadata
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests import fixtures

# Tests

@nose.tools.nottest
def test_to_xml():
    yield export_to_xml, fixtures.foo1, '/tmp/out-foo-1.xml'
    yield export_to_xml, fixtures.inspire1, '/tmp/out-inspire-1.xml'

@nose.tools.nottest
def test_from_xml():
    yield import_from_xml, 'tests/samples/corine_2000.xml'

def export_to_xml(obj, outfile):
    '''Test exporting to XML'''

    obj.to_xml(outfile)

@nose.tools.nottest
def import_from_xml(infile):
    '''Test importing from XML'''

    obj = InspireMetadata()
    obj.from_xml(infile)

    return obj

if __name__ == '__main__':
    export_to_xml(fixtures.inspire1, 'out-1.xml')
    #import_from_xml('samples/3.xml')

    pass
