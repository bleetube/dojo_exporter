from sys import exit
from os import environ, _exit
from platform import node
from json import loads
from urllib.error import URLError
from urllib.request import Request, urlopen
import bitmath

# https://github.com/prometheus/client_python
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from time import sleep

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

    def convert_duration_to_seconds(self, duration: str) -> int:
        """Convert the Dojo uptime duration string (e.g. "028:23:42:58") into seconds."""
        duration = duration.split(":")
        seconds = 0
        seconds += int(duration[0]) * 86400 # days
        seconds += int(duration[1]) * 3600  # hours
        seconds += int(duration[2]) * 60    # minutes
        seconds += int(duration[3])         # seconds
        return int(seconds)

    @REQUEST_TIME.time()
    def collect(self):
        DOJO_JWT = self.get_dojo_jwt( self.DOJO_BASE_URL, self.DOJO_APIKEY )
        DOJO_STATUS = self.get_dojo_status( DOJO_JWT, self.DOJO_BASE_URL, self.DOJO_APIKEY )
        try:
            DOJO_UPTIME=self.convert_duration_to_seconds( DOJO_STATUS["uptime"] )
            DOJO_MEMORY=bitmath.parse_string(DOJO_STATUS["memory"]).bytes
            yield GaugeMetricFamily('dojo_uptime_seconds', 'Dojo tracker uptime', value=DOJO_UPTIME )
            yield GaugeMetricFamily('dojo_memory_bytes', 'Dojo tracker memory consumption in bytes', value=DOJO_MEMORY )
            yield GaugeMetricFamily('dojo_block_height', 'Block height', value=DOJO_STATUS['blocks'] )
            yield GaugeMetricFamily('dojo_ws_clients', 'HTTP Websocket clients', value=DOJO_STATUS['ws']['clients'] )
            yield GaugeMetricFamily('dojo_ws_sessions', 'HTTP Websocket sessions', value=DOJO_STATUS['ws']['sessions'] )
            yield GaugeMetricFamily('dojo_ws_max', 'HTTP Websocket max', value=DOJO_STATUS['ws']['max'] )
            yield GaugeMetricFamily('dojo_indexer_max_height', 'Indexer maximum block height', DOJO_STATUS['indexer']['maxHeight'] )

            # Labels and values are mutually exclusive.
            g = GaugeMetricFamily( "dojo_indexer", "Indexer type and url", labels=[ "type", "url" ])
            # Enforce str() labels because the url can be null/None, resulting in an AttributeError.
            g.add_metric([ str( DOJO_STATUS[ 'indexer' ][ 'type' ]), 
                str( DOJO_STATUS[ 'indexer' ][ 'url' ])],
                1)
            yield g

            # Node name
            n = GaugeMetricFamily( "dojo_platform", "Dojo Node Name", labels=[ "node" ])
            n.add_metric([ node() ], 1)
            yield n

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