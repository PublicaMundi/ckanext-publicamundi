import zope.interface
import zope.schema
import copy
import json
import datetime
import nose.tools
from lxml import etree

from ckan.tests import TestController as BaseTestController
from ckanext.publicamundi.tests.functional import with_request_context

from ckanext.publicamundi.lib.metadata.types import (
    ThesaurusTerms, Thesaurus, InspireMetadata)
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata import xml_serializers
from ckanext.publicamundi.lib.metadata.xml_serializers import object_xml_serialize_adapter
from ckanext.publicamundi.lib.metadata.xml_serializers import xml_serializer_for_object

# Tests

class TestController(BaseTestController):

    @nose.tools.istest
    def test_to_xml(self):
        yield self._to_xml, 'inspire1', '/tmp/inspire1.xml'
        yield self._from_xml, '/tmp/inspire1.xml'

    @nose.tools.istest
    def test_from_xml(self):
        # 3.xml contains wrong thesaurus name, fails as invariant
        yield self._from_xml, 'tests/samples/3.xml', set(['keywords'])
        # 3b.xml fails on temporal extent
        yield self._from_xml, 'tests/samples/3b.xml', set(['temporal_extent'])
        # aktogrammh.xml fails on several fields during validation
        yield self._from_xml, 'tests/samples/aktogrammh.xml', set([
            'languagecode', 'locator', 'contact', 'responsible_party', 'identifier', 'resource_language','temporal_extent'])
        # dhmosia_kthria.xml fails on several fields during validation
        yield self._from_xml, 'tests/samples/dhmosia_kthria.xml', set([
            'languagecode', 'locator', 'contact', 'responsible_party', 'identifier', 'resource_language','temporal_extent'])
        # full.xml fails during etree parse, why?
        #yield self._from_xml, 'tests/samples/full.xml', set([])

    @nose.tools.istest
    def test_to_xsd(self):
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/3.xml', False
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/aktogrammh.xml', True

    @with_request_context('publicamundi-tests', 'index')
    def _to_xml(self, fixture_name, outfile):
        obj = getattr(fixtures, fixture_name)

        ser = xml_serializer_for_object(obj)
        iso_xml = ser.dumps()
        fp = open(outfile, "w")
        fp.write(iso_xml)
        fp.close()

    def _from_xml(self, infile, expected_errs=[]):
        ser = xml_serializer_for_object(InspireMetadata())

        e = etree.parse(infile)
        assert isinstance(e, etree._ElementTree)
        out = ser.from_xml(e)
        print 'out'
        print out
        assert isinstance(out, InspireMetadata)
        assert_faulty_keys(out, expected_errs)

    def _validate_with_xsd(self, fixture_name, xml_file, expected_valid):
        obj = getattr(fixtures, fixture_name)
        
        ser = xml_serializer_for_object(obj)
        xsd = ser.to_xsd(wrap_into_schema=True)

        xsd_validator = etree.XMLSchema(xsd)

        xml = etree.parse(xml_file)
        valid = xsd_validator.validate(xml)
        if expected_valid and not valid:
            errors = xsd_validator.error_log
            print errors
            assert False, 'The XML is invalid: -\n%s' %(errors)
        elif not expected_valid and valid:
            assert False, 'The XML is valid, though expexted invalid'

if __name__ == '__main__':
    pass
