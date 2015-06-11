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
    def test_to_then_from_xml(self):
        yield self._to_xml, 'inspire1', '/tmp/inspire1.xml'
        yield self._from_xml, '/tmp/inspire1.xml'

        yield self._to_xml, 'inspire4', '/tmp/inspire4.xml'
        yield self._from_xml, '/tmp/inspire4.xml'
        yield self._validate_with_xsd, 'inspire4', '/tmp/inspire4.xml', True

    @nose.tools.istest
    def test_from_xml(self):
        # test1.xml contains wrong thesaurus name, fails as invariant
        yield self._from_xml, 'tests/samples/test1.xml', set(['keywords', 'responsible_party', 'contact'])
        # test2.xml fails on temporal extent
        yield self._from_xml, 'tests/samples/test2.xml', set(['languagecode', 'responsible_party', 'contact'])
        # test3.xml fails on several fields during validation
        yield self._from_xml, 'tests/samples/test3.xml', set([
            'responsible_party', 'locator', 'temporal_extent'])

    @nose.tools.istest
    def test_from_xml_real(self):
        # __after: creation date later than publication
        yield self._from_xml, 'tests/samples/12e4e303-6fe8-4f95-b1cb-991b0c3b6c92.xml', set(['__after'])
        # __after: creation date later than publication
        yield self._from_xml, 'tests/samples/d59c2895-49c0-416f-a77e-122459cc8cac.xml', set(['__after'])
        # resource locator not present
        yield self._from_xml, 'tests/samples/57d0f331-6950-4deb-a2f6-30e560915a2e.xml', set(['locator'])
        # valid
        yield self._from_xml, 'tests/samples/9e109365-b9eb-4500-b664-4f3962c4d6e7.xml', set([])

    @nose.tools.istest
    def test_to_xsd(self):
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/test1.xml', False
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/test2.xml', False
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/12e4e303-6fe8-4f95-b1cb-991b0c3b6c92.xml', True
        yield self._validate_with_xsd, 'inspire1', 'tests/samples/57d0f331-6950-4deb-a2f6-30e560915a2e.xml', True

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
