"""
Contains a utility class to perform WCST requests from python
"""
from abc import ABCMeta, abstractmethod
import urllib as url_lib


class WCSTRequest:
    """
    Generic class for WCST requests
    """
    __metaclass__ = ABCMeta
    SERVICE_PARAMETER = "service"
    SERVICE_VALUE = "WCS"
    VERSION_PARAMETER = "version"
    VERSION_VALUE = "2.0.1"
    REQUEST_PARAMETER = "request"

    def get_query_string(self):
        """
        Returns the query string that defines the WCST requests (the get parameters in string format)

        :return: string - containing the request information in KVP syntax
        """
        extra_params = ""
        for key, value in self._get_request_type_parameters().iteritems():
            extra_params += "&" + key + "=" + value
        return self.SERVICE_PARAMETER + "=" + self.SERVICE_VALUE + "&" +\
               self.VERSION_PARAMETER + "=" + self.VERSION_VALUE + "&" +\
               self.REQUEST_PARAMETER + "=" + self._get_request_type() + extra_params

    @abstractmethod
    def _get_request_type_parameters(self):
        """
        Returns the request specific parameters

        :return: dict - containing the needed parameters
        """
        pass

    @abstractmethod
    def _get_request_type(self):
        pass


class WCSTInsertRequest(WCSTRequest):
    """
    Class to perform WCST insert requests
    """

    def __init__(self, coverage_ref, generate_id=False):
        """
        Constructor for the class

        :param coverage_ref: string - the name of the coverage in string format
        :param generate_id: bool - true if a new id should be generated, false otherwise
        """
        self.coverage_ref = coverage_ref
        self.generate_id = generate_id

    def _get_request_type(self):
        return self.__REQUEST_TYPE

    def _get_request_type_parameters(self):
        return {
            self.__GENERATE_ID_PARAMETER: self.__GENERATE_ID_TRUE_VALUE if self.generate_id else self.__GENERATE_ID_FALSE_VALUE,
            self.__COVERAGE_REF_PARAMETER: self.coverage_ref
        }

    __GENERATE_ID_TRUE_VALUE = "new"
    __GENERATE_ID_FALSE_VALUE = "existing"
    __GENERATE_ID_PARAMETER = "useId"
    __COVERAGE_REF_PARAMETER = "coverageRef"
    __REQUEST_TYPE = "InsertCoverage"


class WCSTDeleteRequest(WCSTRequest):
    """
    Class to perform WCST delete requests
    """

    def __init__(self, coverage_ref):
        """
        Constructor for the class

        :param coverage_ref: string -  the name of the coverage in string format
        """
        self.coverage_ref = coverage_ref
        pass

    def _get_request_type(self):
        return self.__REQUEST_TYPE

    def _get_request_type_parameters(self):
        return {
            self.__COVERAGE_REF_PARAMETER: self.coverage_ref
        }

    __COVERAGE_REF_PARAMETER = "coverageId"
    __REQUEST_TYPE = "DeleteCoverage"


class WCSTException(Exception):
    """
    Exception that is thrown when a WCST request has gone wrong
    """

    def __init__(self, exception_code, exception_text, service_call):
        self.exception_code = exception_code
        self.exception_text = exception_text
        self.service_call = service_call
        self.message = self.__str__()

    def __str__(self):
        return "Service Call: " + self.service_call + "\nError Code: " + self.exception_code + \
               "\nError Text: " + self.exception_text


class WCSTExecutor():
    def __init__(self, base_url):
        """
        Constructor class

        :param base_url: string - the base url to the service that supports WCST
        """
        self.base_url = base_url


    def execute(self, request):
        """
        Executes a WCST request and returns the response to it

        :param request: WCSTRequest - the request to be executed
        :return:  string - result with the response from the WCST service
        """
        service_call = self.base_url + "?" + request.get_query_string()
        response = url_lib.urlopen(service_call).read()
        try:
            result = response
        except Exception as ex:
            result = ""
        return result


class WMSFromWCSInsertRequest():
    """
    Class to insert a wcs coverage into wms. This is not a standard way in OGC but a custom method in the
    WMS service offered by rasdaman to allow for automatic insertion
    """

    def __init__(self, wcs_coverage_id):
        """
        Constructor for the class
        @:param wcs_coverage_id the coverage id to be used as a layer
        """
        self.wcs_coverage_id = wcs_coverage_id

    def execute(self, base_url):
        """
        Executes the request and inserts the layer
        @:param base_url the base url to the wms service
        """
        service_call = base_url + "?service=WMS&version=1.3&request=InsertWCSLayer&wcsCoverageId="
        service_call += self.wcs_coverage_id
        service_call += "&withPyramids=true"
        response = url_lib.urlopen(service_call).read()
        return response


class WMSFromWCSDeleteRequest():
    """
    Class to delete a wcs coverage into wms. This is not a standard way in OGC but a custom method in the
    WMS service offered by rasdaman to allow for automatic insertion
    """

    def __init__(self, wcs_coverage_id):
        self.wcs_coverage_id = wcs_coverage_id

    def execute(self, base_url):
        """
        Executes the request and inserts the layer
        @:param base_url the base url to the wms service
        """
        service_call = base_url + "?service=WMS&version=1.3&request=DeleteLayer&layer="
        service_call += self.wcs_coverage_id
        response = url_lib.urlopen(service_call).read()
        return response
