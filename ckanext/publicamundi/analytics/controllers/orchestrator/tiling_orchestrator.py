import json
from lxml import etree
import urllib


class TilingOrchestrator:
    __RETILE_REQUEST = "?service=WCS&version=2.0.1" \
                       "&request=RetileCoverage" \
                       "&coverageId={coverageId}" \
                       "&tilingStrategy={tilingStrategy}" \
                       "&tilingSubsets={tilingSubset}"

    __GET_CAPABILITIES_REQUEST = "?service=WCS&version=2.0.1&request=GetCapabilities"

    __DESCRIBE_COVERAGE_REQUEST = "?service=WCS&version=2.0.1&request=DescribeCoverage&coverageId="

    __PYRAMIDS_REQUEST = "?service=WMS&version=1.3.0&request=GeneratePyramidLayers&layer="

    __RETILING_METHOD = "areaofinterest"

    def __init__(self, analytics_api_endpoint, rasdaman_endpoint):
        self.analytics_api = analytics_api_endpoint
        self.rasdaman_endpoint = rasdaman_endpoint
        self.coverages = None

    def determine_bbox(self):
        response = urllib.urlopen(self.analytics_api + "/parse/bbox").read()
        bboxes = map(lambda x: x['bbox'][0][0] + x['bbox'][0][2], json.loads(response))
        return bboxes

    def adjust(self):
        self.retile_coverages()

    def adjust_description(self):
        return json.dumps(self.retile_coverages(True))

    def adjust_pyramids(self, layer):
        request = self.rasdaman_endpoint + self.__PYRAMIDS_REQUEST + layer
        return urllib.urlopen(request).read()

    def retile_coverages(self, describe=False):
        bboxes = self.determine_bbox()
        coverages = self.get_coverages()
        description_contents = []
        for bbox in bboxes:
            for coverage in coverages:
                if self.bbox_contains(coverage['bbox'], bbox):
                    if describe:
                        description_contents.append({"name": coverage['name'], "bbox": str(bbox)})
                    else:
                        self.execute_tiling_request(coverage['name'], self.__RETILING_METHOD, str(bbox))
        if describe:
            return description_contents

    def bbox_contains(self, bbox1, bbox2):
        if bbox1[0] < bbox2[0] and bbox1[1] < bbox2[1] and bbox1[2] > bbox2[2] and bbox1[3] > bbox1[3]:
            return True
        return False

    def get_coverages(self):
        if self.coverages is None:
            xmlstr = urllib.urlopen(self.rasdaman_endpoint + self.__GET_CAPABILITIES_REQUEST).read()
            root = etree.fromstring(xmlstr)
            self.coverages = map(lambda x: self.get_coverage_description(x.text),
                                 root.xpath("//wcs:CoverageId", namespaces=self._get_ns()))
        return self.coverages

    def get_coverage_description(self, coverage):
        xmlstr = urllib.urlopen(self.rasdaman_endpoint + self.__DESCRIBE_COVERAGE_REQUEST + coverage).read()
        root = etree.fromstring(xmlstr)
        geo_low = map(lambda x: float(x),
                      root.xpath("//gml:Envelope/gml:lowerCorner", namespaces=self._get_ns())[0].text.strip().split(
                          " "))
        geo_high = map(lambda x: float(x),
                       root.xpath("//gml:Envelope/gml:upperCorner", namespaces=self._get_ns())[0].text.strip().split(
                           " "))
        return {"name": coverage, "bbox": geo_low + geo_high}

    def execute_tiling_request(self, coverage_id, tiling_strategy, tiling_subset):
        request = self.rasdaman_endpoint + "?" + self.__RETILE_REQUEST.replace("{coverageId}", coverage_id) \
            .replace("{tilingStrategy}", tiling_strategy) \
            .replace("{tilingSubset}", tiling_subset)
        response = urllib.urlopen(request).read()
        return response

    @staticmethod
    def _get_ns():
        return {"gml": "http://www.opengis.net/gml/3.2", "gmlcov": "http://www.opengis.net/gmlcov/1.0",
                "swe": "http://www.opengis.net/swe/2.0", "wcs": "http://www.opengis.net/wcs/2.0",
                "gmlrgrid": "http://www.opengis.net/gml/3.3/rgrid"}


if __name__ == "__main__":
    tl = TilingOrchestrator("http://172.16.182.153/api/analytics",
                            "http://rasdaman.dev.publicamundi.eu:8080/rasdaman/ows")
    tl.retile_coverages()


