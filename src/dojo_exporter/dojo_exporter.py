from sys import exit
from os import environ, _exit
from json import loads
from urllib.error import URLError
from urllib.request import Request, urlopen

# https://github.com/prometheus/client_python
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, SummaryMetricFamily, REGISTRY
from time import sleep
import random

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

class DojoCollector(object):
    def __init__(self) -> None:
        """Read environment variables."""
        if environ.get("DOJO_APIKEY"):
            self.DOJO_APIKEY = environ.get("DOJO_APIKEY")
        else:
            quit( "Error: DOJO_APIKEY environment variable is required." )

        if environ.get("NET_DMZ_NGINX_IPV4"):
            self.NET_DMZ_NGINX_IPV4 = environ.get("NET_DMZ_NGINX_IPV4")
        else:
            self.NET_DMZ_NGINX_IPV4 = "172.29.1.3"

        if environ.get("DOJO_BASE_URL"):
            self.DOJO_BASE_URL = environ.get("DOJO_BASE_URL")
        else:
            self.DOJO_BASE_URL = f"http://{self.NET_DMZ_NGINX_IPV4}"

    def get_dojo_jwt(self, DOJO_BASE_URL: str, DOJO_APIKEY: str) -> str:
        """Get a JSON Web Token (JWT) by making one http request to a self-hosted Samourai Dojo instance."""
        jwt_request_url = f"{DOJO_BASE_URL}/v2/auth/login"
        jwt_request_params = f"apikey={DOJO_APIKEY}"
        jwt_request = Request( 
            jwt_request_url, 
            data=bytes( jwt_request_params, encoding="utf-8" ),
        )
        try:
            with urlopen( jwt_request ) as url:
                # Convert the http body response (string) into a dictionary.
                jwt_result = loads( url.read().decode() )
        except URLError as e:
            print( f"jwt_request URLError: {jwt_request_url} \n{e}")
            return None
        except Exception as e:
            print( f"jwt_request Exception: {jwt_request_url} \n{e}")
            return None
        
        try:
            DOJO_JWT = jwt_result["authorizations"]["access_token"]
            return DOJO_JWT
        except Exception as e:
            print( f"jwt_result Exception: {jwt_result} \n{e}")
            return None

    def get_dojo_status(self, DOJO_JWT: str, DOJO_BASE_URL: str, DOJO_APIKEY: str) -> dict:
        """Get the status of a self-hosted Samourai Dojo instance by making one http request."""
        status_request_url = f"{DOJO_BASE_URL}/v2/status?at={DOJO_JWT}"
        status_request = Request( status_request_url )
        try:
            with urlopen( status_request ) as url:
                # Convert the http body response (string) into a dictionary.
                return loads( url.read().decode() )
        except URLError as e:
            # Corner case: If you see "<urlopen error [Errno -5] No address associated with hostname>"
            # It's a DNS error and you might just need to set a static hosts file entry for your Dojo FQDN.
            print( f"URLError: {status_request_url} \n{e}")
            return None
        except Exception as e:
            print( f"Exception: {status_request_url} \n{e}")
            return None

    @REQUEST_TIME.time()
    def collect(self):
        DOJO_JWT = self.get_dojo_jwt( self.DOJO_BASE_URL, self.DOJO_APIKEY )
        DOJO_STATUS = self.get_dojo_status( DOJO_JWT, self.DOJO_BASE_URL, self.DOJO_APIKEY )
        try:
            yield GaugeMetricFamily('dojo_ws_clients', 'Block height', value=DOJO_STATUS['ws']['clients'] )
            yield GaugeMetricFamily('dojo_ws_clients', 'Block height', value=DOJO_STATUS['ws']['sessions'] )
            yield GaugeMetricFamily('dojo_ws_clients', 'Block height', value=DOJO_STATUS['ws']['max'] )
            yield GaugeMetricFamily('dojo_bitcoind_blocks', 'Block height', value=DOJO_STATUS['blocks'] )
            yield GaugeMetricFamily('dojo_indexer_max_height', 'Indexer maximum block height', value=DOJO_STATUS['indexer']['maxHeight'] )
            # TODO: 
            # - DOJO_STATUS['uptime'] needs to be converted to seconds.
            # - DOJO_STATUS['memory'] needs to be converted to bytes.
            # - DOJO_STATUS['indexer']['type'] needs to be converted to a label.
            # - DOJO_STATUS['indexer']['url'] needs to be converted to a label.

            print( DOJO_STATUS )
        except Exception as e:
            print( f"Exception: {DOJO_STATUS} \n{e}")
            return None

    

def main():
    """Start the prometheus client child process and register the DojoCollector to it."""

    # Optional environment variable to set the bind options.
    if environ.get("METRICS_PORT"):
        METRICS_PORT = environ.get("METRICS_PORT")
    else:
        METRICS_PORT = 9102
    if environ.get("METRICS_BIND"):
        METRICS_BIND = environ.get("METRICS_BIND")
    else:
        METRICS_BIND = "127.0.0.1"

    # Prometheus client listener (default: 127.0.0.1:9102)
    start_http_server(METRICS_PORT, METRICS_BIND)
    REGISTRY.register(DojoCollector())

#   dojo_collector = DojoCollector()
#   dojo_collector.collect()

    # This is a hack to prevent the child process from exiting.
    while True:
        sleep(10)

if __name__ == '__main__':
    try:
        main()
    # Catch cntrl+c
    except KeyboardInterrupt:
        try:
            exit(0)
        except SystemExit:
            _exit(0)