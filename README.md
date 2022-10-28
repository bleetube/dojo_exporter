# Basic openmetrics for Samourai Dojo

A component for monitoring your Dojo health, which can be integrated with a self-hosted SRE stack. If you don't have one set up already, this won't be useful to you. It's basically a wrapper on two calls to `curl`.

## Installation and Usage

``` bash
pip install <TBD>
```

Define the connection parameters to your Dojo via environment variables. There are multiple ways you can set it up. One example is to create a `.env` file with the following contents:

```bash
export DOJO_APIKEY=<password>                       # Required
export NET_DMZ_NGINX_IPV4=172.29.1.3                # Optional. Default value shown
export DOJO_BASE_URL=http://${NET_DMZ_NGINX_IPV4}   # Optional. Default value shown
```

I would recommend running this as an unprivileged user via systemd (or anything comparable):

```bash
useradd -ms $(which nologin) dojo_exporter
```

`/etc/systemd/system/dojo_exporter.service`:

```systemd
[Unit]
Description=dojo_exporter

[Service]
User=dojo_exporter
Group=dojo_exporter
ExecStart=python -m <TBD>

[Install]
WantedBy=multi-user.target
```

## Development

Clone the repo and install dependencies into a local virtual environment:

```bash
git clone git@github.com/bleebl33/dojo_exporter
cd dojo_exporter
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --editable .
source .env
```

You can just declare `DOJO_PATH` and let the script learn all the other parameters. It defaults to `$HOME/dojo`, so if that's where you install Dojo then you don't have to declare any variables.
