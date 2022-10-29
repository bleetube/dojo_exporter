import json
from os import environ
from urllib.error import URLError

# https://github.com/prometheus/client_python
from prometheus_client import start_http_server, Summary, Gauge
#import random
#import time

from urllib.request import Request, urlopen, urlretrieve, build_opener, install_opener
# setup urllib user-agent (required for urlretrieve)
#opener=build_opener()
#opener.addheaders=[('User-Agent','Mozilla/5.0')]
#install_opener(opener)

def get_dojo_jwt(DOJO_BASE_URL: str, DOJO_APIKEY: str) -> str:
    jwt_request_url = f"{DOJO_BASE_URL}/v2/auth/login"
    jwt_request_params = f"apikey={DOJO_APIKEY}"
    jwt_request = Request( 
        jwt_request_url, 
        data=bytes( jwt_request_params, encoding="utf-8" ),
    )
    try:
        with urlopen( jwt_request ) as url:
            # Convert the http body response (string) into a dictionary.
            return json.loads( url.read().decode() )
    except URLError as e:
        print( f"URLError: {jwt_request_url} \n{e}")
        return None
    except Exception as e:
        print( f"Exception: {jwt_request_url} \n{e}")
        return None

def update_metrics():
#   derp.labels('derp').set( derp )
    pass


def main():
    if environ.get("DOJO_APIKEY"):
        DOJO_APIKEY = environ.get("DOJO_APIKEY")
    else:
        quit( "Error: DOJO_APIKEY environment variable is required." )

    if environ.get("NET_DMZ_NGINX_IPV4"):
        NET_DMZ_NGINX_IPV4 = environ.get("NET_DMZ_NGINX_IPV4")
    else:
        NET_DMZ_NGINX_IPV4 = "172.29.1.3"

    if environ.get("DOJO_BASE_URL"):
        DOJO_BASE_URL = environ.get("DOJO_BASE_URL")
    else:
        DOJO_BASE_URL = f"http://{NET_DMZ_NGINX_IPV4}"

    dojo_jwt = get_dojo_jwt( DOJO_BASE_URL, DOJO_APIKEY )
    if dojo_jwt:
        print( f"dojo_jwt: {dojo_jwt}")
    else:
        quit( "We here now." )
    
    # listen for requests
#   start_http_server(9102, '127.0.0.1')

if __name__ == '__main__':
    main()