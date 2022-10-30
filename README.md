# Prometheus openmetrics for Dojo

![sample Grafana dashboard](https://raw.githubusercontent.com/bleebl33/dojo_exporter/main/dashboards/dojo_exporter-01.jpg)

A devops component for monitoring your self-hosted [Samourai Dojo](https://code.samourai.io/dojo/samourai-dojo), which can be integrated with your self-hosted SRE stack. If you don't have one set up already, this won't be useful to you. It's basically a wrapper on two calls to `curl`.

## Installation and Usage

``` bash
pip install dojo-exporter
```

Define the connection parameters to your Dojo via environment variables. There are multiple ways you can set it up. One example is to create an `.env` file with the following contents:

```bash
export DOJO_APIKEY=<password>                       # Required
export NET_DMZ_NGINX_IPV4=172.29.1.3                # Optional. Default value shown
export DOJO_BASE_URL=http://${NET_DMZ_NGINX_IPV4}   # Optional. Default value shown
```

I would recommend running this as an unprivileged user via systemd (or anything comparable):

```bash
useradd -mb /opt -k /dev/null -s $(which nologin) dojo_exporter
```

Create `/etc/systemd/system/dojo_exporter.service`:

```systemd
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
source .env
dojo_exporter
```

## Roadmap

- Include tests
- Change `print()` messages into sensible logging with configuration debug levels.
- Review Dojo `/admin/dmt/status/status.js` to possibly discover more metrics.
- Dockerfile

## Security

This goes without saying for most cases: A number of necessray dependencies are used which causes nominal exposure to [supply chain](https://cloud.google.com/software-supply-chain-security/docs/attack-vectors) attacks. The risk would be that the Dojo apikey is leaked, which could compromise user privacy. There should be no risk of losing funds as private keys are never transmitted to the dojo. You should never run this software on a machine with a hot wallet.
