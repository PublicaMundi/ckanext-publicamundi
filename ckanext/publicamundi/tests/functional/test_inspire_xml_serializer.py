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
from ckanext.publicamundi.lib.metadata.xml_serializers import object_xml_serialize_adapter
from ckanext.publicamundi.lib.metadata.xml_serializers import xml_serializer_for_object

# Tests

class TestController(BaseTestController):

    @nose.tools.istest
    def test_to_xml(self):
        yield self._to_xml, fixtures.inspire1, '/tmp/inspire1.xml'

    @nose.tools.istest
    def test_from_xml(self):
        # 3.xml contains wrong thesaurus name
        yield self._from_xml, 'tests/samples/3.xml', set(['keywords'])
        # aktogrammh.xml fails on several fields during validation
        yield self._from_xml, 'tests/samples/aktogrammh.xml', set(['languagecode', 'locator', 'contact', 'responsible_party', 'identifier', 'resource_language'])
        # dhmosia_kthria.xml fails on several fields during validation
        yield self._from_xml, 'tests/samples/dhmosia_kthria.xml', set(['languagecode', 'locator', 'contact', 'responsible_party', 'identifier', 'resource_language'])
        # full.xml fails during etree parse, why?
        #yield self._from_xml, 'tests/samples/full.xml', set([])

    @nose.tools.istest
    def test_to_xsd(self):
        yield self._validate_with_xsd, fixtures.inspire1, 'tests/samples/3.xml', False
        yield self._validate_with_xsd, fixtures.inspire1, 'tests/samples/aktogrammh.xml', True

    @with_request_context('publicamundi-tests', 'index')
    def _to_xml(self, obj, outfile):
        #obj = InspireMetadata()
        ser = xml_serializer_for_object(obj)
        #ser.to_xml()
        iso_xml = ser.dumps()
        #assert isinstance(iso_xml, str)
        #print '1'
        #print iso_xml
        fp = open(outfile, "w")
        fp.write(iso_xml)
        fp.close()

    def _from_xml(self, infile, expected_errs=[]):
        ser = xml_serializer_for_object(InspireMetadata())

        e = etree.parse(infile)
        assert isinstance(e, etree._ElementTree)
        out = ser.from_xml(e)
        assert isinstance(out, InspireMetadata)
        #print 'out='
        #print out.keywords[0].thesaurus
        #print 'correct='
        #print fixtures.inspire1.keywords[1].thesaurus
        assert_faulty_keys(out,
        expected_errs)

        #errors = out.validate()
        #assert not errors

    def _validate_with_xsd(self, obj, xml_file, expected_valid):
        ser = xml_serializer_for_object(obj)
        xsd = ser.to_xsd(wrap_into_schema=True)

        xsd_validator = etree.XMLSchema(xsd)

        #path = os.path.dirname(os.path.dirname('/home/ckaner/xsd_files/1'))
        #path = os.path.dirname(os.path.dirname(__file__))
        #data_file = os.path.join(path, DATA_FILE)

        xml = etree.parse(xml_file)
        if not expected_valid == xsd_validator.validate(xml):
            errors = xsd_validator.error_log
            raise TypeError('Invalid XML\nerrors:\n', errors)

        #out = ser.from_xml(e)
        #assert isinstance(out, InspireMetadata)
        #errors = out.validate()
        #assert not errors

if __name__ == '__main__':
    pass
