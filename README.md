# Prometheus openmetrics for Dojo

![sample Grafana dashboard](https://github.com/bleebl33/dojo_exporter/raw/main/dashboards/dojo_exporter-01.jpg)

A devops component for monitoring your self-hosted [Samourai Dojo](https://code.samourai.io/dojo/samourai-dojo), which can be integrated with your self-hosted SRE stack. If you don't have one set up already, this won't be useful to you. It's a simple python script that gets the JWT, calls the status endpoint, then transforms the results into prometheus metrics.

## Installation and Usage

``` bash
pip install --upgrade pip
pip install dojo-exporter
```

Define the connection parameters to your Dojo via environment variables. There are multiple ways you can set it up. One example is to create an `.env` file with the following contents:

```bash
DOJO_APIKEY=<password>                     # Required
NET_DMZ_NGINX_IPV4=172.29.1.3              # Optional. Default value shown
DOJO_BASE_URL=http://${NET_DMZ_NGINX_IPV4} # Optional. Default value shown
METRICS_BIND=127.0.0.1                     # Optional. Default value shown
METRICS_PORT=9102                          # Optional. Default value shown
```

I would recommend running this as an unprivileged user via systemd (or anything comparable):

```bash
useradd -mb /opt -k /dev/null -s $(which nologin) dojo_exporter
```

Create `/etc/systemd/system/dojo_exporter.service`:

```ini
[Unit]
Description=Basic openmetrics for Samourai Dojo

[Service]
User=dojo_exporter
Group=dojo_exporter
EnvironmentFile=/opt/dojo_exporter/.env
ExecStart=dojo_exporter
Restart=on-failure
RestartSec=5m

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
dojo_exporter
```

Note that there is a difference between `source .env` and systemd EnvironmentFile which is that you'll need to have the export keyword. i.e. `export DOJO_APIKEY=<password>`

## Roadmap

- Include tests
- Change `print()` messages into sensible logging with configuration debug levels.
- Review Dojo `/admin/dmt/status/status.js` to possibly discover more metrics.
- Dockerfile

## Security

This goes without saying for most cases: A number of necessary dependencies are used which causes nominal exposure to [supply chain](https://cloud.google.com/software-supply-chain-security/docs/attack-vectors) attacks. The risk would be that the Dojo apikey is leaked, which could compromise user privacy. There should be no risk of losing funds as private keys are never transmitted to the dojo. You should never run this software on a machine with a hot wallet.

Furthermore you can harden the installation by keeping it in a virtual environment, rather than installing it globally. Afterwards you can find the path of the command with `which dojo_exporter` and then set your systemd service up accordingly. e.g. 

```ini
ExecStart=/opt/dojo_exporter/.venv/bin/dojo_exporter
```
