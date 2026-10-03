<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-system-services

A NetBox 4.6 plugin: a **native source of truth for a network device's management-plane
services** — system identity, SNMP, syslog, NTP, and the device's own stub DNS resolver.

This replaces the unstructured `config_context` blob these settings used to live in. Every
field is a real column, so the `ansible-tofu` reconcilers read each service back 1:1 with
zero loss.

## Why

`config_context` is free-form JSON: it has no schema, no validation, no per-field change
log, no filtering, and no REST contract. Management-plane services (SNMP/syslog/NTP/DNS) are
structured and repeat per device, so they belong in real models — queryable, change-logged,
and lossless — exactly like firewall rules belong in `netbox-pf` instead of a config blob.

## Model

Each feature is a **per-device singleton config** (`OneToOneField` to `dcim.Device`,
`on_delete=CASCADE`) plus **child rows** where the data repeats:

- **SystemConfig** — `default_gateway`, `location` (sysLocation), `contact` (sysContact),
  `config_history_count` (configuration revisions the device keeps; blank = the device default).
  Hostname is `device.name`, never duplicated.
- **SNMPConfig** — `enabled`, `listen_interface`. sysContact/sysLocation are read from
  SystemConfig, not duplicated.
  - **SNMPCommunity** (FK) — `name` (logical key), `access` (ro/rw), `restricted`.
  - **SNMPTrapTarget** (FK) — `target`, `port`, `version` (v1/v2c), `community_ref`.
- **SyslogConfig** — `severity`, `facility`, `retention_days`.
  - **SyslogServer** (FK) — `host`, `port`, `transport` (udp/tcp/tls).
- **NTPConfig** — `enabled`, `broadcast`, `serve_lan`.
  - **NTPServer** (FK) — `host`, `prefer`.
- **DNSResolverConfig** — `mode` (static/dhcp), `nameservers` (ordered array),
  `search_domains` (ordered array). The device's **own** resolver, **not** authoritative DNS
  zones (those are netbox-dns's job).

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Secret policy

SNMP community strings and trap-target credentials are **never** stored here. `SNMPCommunity.name`
and `SNMPTrapTarget.community_ref` are **logical keys** that look the actual secret up in
**OpenBao**. NetBox holds the structure; OpenBao holds the secret.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-system-services   # or: pip install -e .
# add "netbox_system_services" to PLUGINS in configuration.py
python manage.py migrate netbox_system_services
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test
framework. See `CLAUDE.md`.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_system_services --keepdb -v2
```

## License

AGPL-3.0-or-later.
