import zope.interface
import zope.schema
import copy
import json
import datetime
import nose.tools
from lxml import etree

from ckan.tests import TestController as BaseTestController
from ckanext.publicamundi.tests.functional import with_request_context

from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import ThesaurusTerms, Thesaurus
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import InspireMetadata
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests import fixtures
from ckanext.publicamundi.lib.metadata import xml_serializers
from ckanext.publicamundi.lib.metadata.xml_serializers import xml_serializer_for_object

# Tests

class TestController(BaseTestController):
    
    @nose.tools.istest
    def test_to_xml(self):
        yield self._to_xml, 'inspire1', '/tmp/fixture-inspire1.xml'

    @nose.tools.istest
    def test_from_xml(self):
        yield self._from_xml, 'tests/samples/3.xml'
        yield self._from_xml, 'tests/samples/aktogrammh.xml'

    @with_request_context('publicamundi-tests', 'index')
    def _to_xml(self, fixture_name, outfile):
        '''Load an InspireMetadata fixture object and dump it as XML.
        '''

        obj = getattr(fixtures, fixture_name)
        assert isinstance(obj, InspireMetadata)
        ser = xml_serializer_for_object(obj)
        assert ser

        s = ser.dumps()
        assert isinstance(s, unicode)
        
        with open(outfile, "w") as ofp:
            ofp.write(s)
            ofp.close()

        #e = ser.to_xml()
        #assert e is not None

        return

    @with_request_context('publicamundi-tests', 'index')
    def _from_xml(self, infile):
        '''Instantiate an InspireMetadata object from an XML dump.
        '''
        
        ser = xml_serializer_for_object(InspireMetadata())

        e = etree.parse(infile)
        assert isinstance(e, etree._ElementTree)
        
        o = ser.from_xml(e)
        assert isinstance(o, InspireMetadata)
        
        js = o.to_json(indent=4)
        print ' -- Loaded object from %s -- ' %(infile)
        print js

        errors = o.validate(dictize_errors=True)
        assert not errors

