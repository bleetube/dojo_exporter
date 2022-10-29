#!/bin/bash
# Demonstrates basic curl commands necessary to acquire current Dojo status.

###
# Option 1: We can define the necessary parameters here.
###
#DOJO_APIKEY=$(pass tests/DOJO_APIKEY)  # read apikey from password manager
#NET_DMZ_NGINX_IPV4=172.29.1.3          # Default value is 172.29.1.3

###
# Option 2: We can learn the necessary parameters by sourcing dojo configuration directly.
#           Obviously, this only works if we're running on the same machine as the dojo.
###
DOJO_PATH=$HOME/dojo
if [ -f "${DOJO_PATH}/docker/my-dojo/conf/docker-node.conf" ]; then
  source "${DOJO_PATH}/docker/my-dojo/conf/docker-node.conf"
  source "${DOJO_PATH}/docker/my-dojo/.env"
fi

# URL to Dojo tracker API
#DOJO_BASE_URL=http://${NET_DMZ_NGINX_IPV4}
# Or if you're polling remotely via a reverse proxy with tls 1.3, like me:
#DOJO_BASE_URL=https://dojo.example.com
# (Optional) You could also poll via the onion address through your tor daemon's socks5 proxy.
# Although it could fail on false positives if tor connectivity is not optimal.
#SOCKS="--socks5-hostname 127.0.0.1:9050"
#DOJO_BASE_URL=http://e2412ed3841ed782f4a50130e1daec77ef9596b4a42c26d7719294cb6facf5fd.onion
# In hindsight, it's totally crazy to poll the onion address directly.

# Sanity checks
if [[ ! $(id -u) ]] ; then echo "Do not run this as root. You're insane." ; exit 1 ; fi
if [[ ! $(which curl) ]] ; then echo "Error: Missing required dependency: curl" ; exit 1 ; fi
if [[ ! $(which jq) ]] ; then echo "Error: Missing required dependency: jq" ; exit 1 ; fi

# curl once to acquire a JSON Web Token from Dojo
TOKEN=$(curl ${SOCKS} -q "${DOJO_BASE_URL}/v2/auth/login" \
  --data-raw "apikey=${DOJO_APIKEY}"  2>/dev/null |
  jq -r '.authorizations.access_token')

if [[ "${TOKEN}" ]]; then
  # curl again using the JWT to get the status of the Dojo instance
  curl ${SOCKS} -q "${DOJO_BASE_URL}/v2/status?at=${TOKEN}" 2>/dev/null | jq
else
  echo "Error: Failed to acquire a token from Dojo. Did you configure the API key and base url?"
fi
 
