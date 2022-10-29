import json
from os import environ
from urllib.error import URLError
from urllib.request import Request, urlopen, urlretrieve, build_opener, install_opener

# https://github.com/prometheus/client_python
from prometheus_client import start_http_server, Summary, Gauge

def get_dojo_jwt(DOJO_BASE_URL: str, DOJO_APIKEY: str) -> str:
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
            jwt_result = json.loads( url.read().decode() )
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

def get_dojo_status(DOJO_JWT: str, DOJO_BASE_URL: str, DOJO_APIKEY: str) -> dict:
    """Get the status of a self-hosted Samourai Dojo instance by making one http request."""
    status_request_url = f"{DOJO_BASE_URL}/v2/status?at={DOJO_JWT}"
    status_request = Request( status_request_url )
    try:
        with urlopen( status_request ) as url:
            # Convert the http body response (string) into a dictionary.
            return json.loads( url.read().decode() )
    except URLError as e:
        # Corner case: If you see "<urlopen error [Errno -5] No address associated with hostname>"
        # It's a DNS error and you might just need to set a static hosts file entry for your Dojo FQDN.
        # Most people don't use FQDNs for their Dojo instances, so this is a rare error.
        print( f"URLError: {status_request_url} \n{e}")
        return None
    except Exception as e:
        print( f"Exception: {status_request_url} \n{e}")
        return None

def get_dojo_metrics():
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

    DOJO_JWT = get_dojo_jwt( DOJO_BASE_URL, DOJO_APIKEY )
    DOJO_STATUS = get_dojo_status( DOJO_JWT, DOJO_BASE_URL, DOJO_APIKEY )
    print( DOJO_STATUS )

    quit( "We here now." )
#   derp.labels('derp').set( derp )


    
def main():
    get_dojo_metrics()

    # listen for requests
#   start_http_server(9102, '127.0.0.1')

if __name__ == '__main__':
    main()