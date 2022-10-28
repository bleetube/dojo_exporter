#!/usr/bin/env python
# https://github.com/prometheus/client_python
# source .venv/prometheus_client
# TODO: handle web request failures gracefully. otherwise the script crashes.
import json
from urllib.request import urlopen
from os import environ

# https://github.com/prometheus/client_python
from prometheus_client import start_http_server, Summary, Gauge
import random
import time

def get_json_data(uri):
    with urlopen( uri ) as url:
        return json.loads( url.read().decode() )

def update_metrics():
#   derp.labels('derp').set( derp )
    pass


def main():
    # Define the path to our Dojo installation or assume the default path of $HOME/dojo
    DOJO_PATH = environ.get("DOJO_PATH", f"{ environ.get( 'HOME' )}/dojo")

    if not environ.get("DOJO_APIKEY"):
        quit( "ERROR: DOJO_APIKEY environment variable must be set." )

    # listen for requests
    start_http_server(9102, '127.0.0.1')

    while True:
        update_metrics()
        time.sleep(30)

if __name__ == '__main__':
    main()