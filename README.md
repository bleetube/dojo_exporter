# Basic openmetrics for Samourai Dojo

A component for monitoring your Dojo health, which can be integrated with a self-hosted SRE stack. If you don't have one set up already, this won't be useful to you. It's basically a wrapper on two calls to `curl`.

## Installation and Usage

``` bash
pip install <placeholder>
```

Define the connection parameters to your Dojo via environment variables. There are multiple ways you can set it up:

```bash
export DOJO_APIKEY=<password>                       # Required
export NET_DMZ_NGINX_IPV4=172.29.1.3                # Optional. Default value shown
export DOJO_BASE_URL=http://${NET_DMZ_NGINX_IPV4}   # Optional. Default value shown
```

You can alternatively just declare `DOJO_PATH` and let the script learn all the other parameters. It defaults to `$HOME/dojo`, so if that's where you install Dojo then you don't have to declare any variables.

## Development

Clone the repo and install dependencies into a local virtual environment:

```bash
git clone git@<placeholder>
cd <placeholder>
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --editable .
source .env
```
