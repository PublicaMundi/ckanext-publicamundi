import json
import urllib


class ServerOrchestrator:
    __INCREASE_SERVERS_REQUEST = "?service=rasdaman&operation=SetWorkerServers&workers="

    __NUMBER_OF_SERVERS_REQUEST = "?service=rasdaman&operation=GetWorkerServers"

    __CACHE_CHANGE = "?service=rasdaman&operation=SetCache&wcs={wcs}&wms={wms}"

    __ANALYTICS_SERVICE_REQUEST = "/parse/services"

    def __init__(self, analytics_api_endpoint, rasdaman_endpoint):
        self.analytics_api = analytics_api_endpoint
        self.rasdaman_endpoint = rasdaman_endpoint

    def adjust_description(self):
        print self.get_new_number_of_servers()

    def adjust_cache(self, wcs, wms):
        request = self.rasdaman_endpoint + self.__CACHE_CHANGE.replace("{wcs}", str(wcs)).replace("{wms}", str(wms))
        return urllib.urlopen(request)

    def adjust(self, number):
        self.set_worker_servers(number)

    def get_new_number_of_servers(self):
        pattern = self.get_access_pattern()
        workers = self.get_worker_server_numbers()
        new_workers = workers + workers * pattern
        return new_workers

    def get_access_pattern(self):
        request = self.analytics_api + self.__ANALYTICS_SERVICE_REQUEST
        accesses = json.loads(urllib.urlopen(request).read())
        previous_access = 0
        total = 0
        direction = 0
        for service_access in accesses:
            current_access = service_access['rasdaman'] + service_access['rasdaman_wcs'] + service_access[
                'rasdaman_wms'] + service_access['rasdaman_wcps']
            if previous_access != 0:
                direction += previous_access - current_access
            previous_access = current_access
            total += current_access
        return float(direction) / float(total)

    def get_worker_server_numbers(self):
        request = self.rasdaman_endpoint + self.__NUMBER_OF_SERVERS_REQUEST
        workers = 10
        try:
            workers = int(urllib.urlopen(request).read())
        except:
            pass
        return workers

    def set_worker_servers(self, number):
        request = self.rasdaman_endpoint + self.__INCREASE_SERVERS_REQUEST + str(number)
        return urllib.urlopen(request).read()


if __name__ == "__main__":
    s = ServerOrchestrator("http://172.16.182.153/api/analytics",
                           "http://rasdaman.dev.publicamundi.eu:8080/rasdaman/ows")
    print s.adjust()