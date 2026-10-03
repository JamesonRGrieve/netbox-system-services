# netbox-system-services — Agent Operating Guide

Adapted from the sibling `../netbox-pf` plugin (same engineering + test discipline),
re-targeted to **management-plane services** instead of firewall rules.

`netbox-system-services` is an **AGPL-3.0** NetBox 4.6 plugin: a **native source of truth for
a network device's management-plane services** — system identity (sysName via `device.name`,
sysLocation, sysContact, default gateway), SNMP (agent + communities + trap targets), syslog
(severity/facility/retention + remote servers), NTP (client/broadcast/serve-LAN roles +
upstream peers), and the device's **own stub DNS resolver** (mode + ordered nameservers +
search domains). It replaces the unstructured `config_context` blob these settings lived in,
giving every field a real column so the `ansible-tofu` reconcilers read each service back 1:1.

**Secret policy (load-bearing):** SNMP community strings and trap-target credentials are
**never** stored here. `SNMPCommunity.name` and `SNMPTrapTarget.community_ref` are *logical
keys* that resolve the actual secret in **OpenBao**. NetBox holds the structure; OpenBao holds
the secret.

**DNS scope:** `DNSResolverConfig` models only the resolver the **device itself** uses. It is
**not** authoritative DNS zones — those are `netbox-dns`'s job.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter
  — never an optional one with an inline presence check.
- Any time you modify a source file, ensure its accompanying test under
  `netbox_system_services/tests/` contains **comprehensive tests for the change WITHOUT MOCKS**,
  so `manage.py test netbox_system_services` discovers them, and update any `.md` in the same
  directory that references the changed code.
- Write concise code (avoid obvious comments; use one-liners where possible).
- Critically analyze requirements and ask all necessary clarifying questions before
  implementing or refactoring.
- Phrase documentation for yourself (AI) and for autistic/ADHD humans: a clear architectural
  summary you could reconstruct the code from with 95% accuracy, with minimal snippets — **not**
  usage examples (the browsable REST/GraphQL schema is the usage reference).

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Store an SNMP community string or any other secret in a model field. Only logical
  names/refs that key OpenBao.
- Duplicate `sysName`/`sysContact`/`sysLocation`: hostname is `device.name`; contact/location
  are on `SystemConfig` only and read from there by SNMP.
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test instead of fixing the root cause.
- Fix broken functionality while keeping the broken path as a fallback.
- Re-implement existing functionality in a second location to bypass the original.
- Use bandaid fixes instead of fixing the core functionality.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests
  run against a **real test database** via NetBox's Django test framework.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — **never** `import datetime`.
- Imports are package-relative inside `netbox_system_services` (`from .models import SNMPConfig`),
  never `from netbox_system_services.models import ...`.
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, change logging,
  GraphQL — for free).
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_system_services`, `base_url='system-services'`, min/max NetBox version |
| `choices.py` | `ChoiceSet`s: SNMP access/version, syslog severity/facility/transport, DNS resolver mode |
| `models.py` | the 9 service models (see §Model) |
| `migrations/` | hand-authored initial migration (NetBox disables makemigrations in prod); verify with `makemigrations --check --dry-run` on an ephemeral NetBox |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST API (`NetBoxModelViewSet`) — the contract `ansible-tofu` reads |
| `filtersets.py` | `NetBoxModelFilterSet` per model (drives API + UI filtering) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py` | UI layer (generic NetBox views; no custom templates) |
| `graphql/` | placeholder (no GraphQL type yet, mirroring netbox-pf) |

### Model — the management-plane SoT (lossless by construction)
Per-device singleton configs are `OneToOneField` to `dcim.Device` (`on_delete=CASCADE`); the
repeating data hangs off them as FK child rows.

- **SystemConfig** (1:1 Device): `default_gateway`, `location`, `contact`; `config_history_count` (configuration revisions the device keeps — OPNsense `<system><backupcount>`; null = device default, min 1).
- **SNMPConfig** (1:1 Device): `enabled`, `listen_interface`.
  - **SNMPCommunity** (FK SNMPConfig): `name` (OpenBao key), `access`, `restricted`; unique per config+name.
  - **SNMPTrapTarget** (FK SNMPConfig): `target`, `port`, `version`, `community_ref` (OpenBao key).
- **SyslogConfig** (1:1 Device): `severity`, `facility`, `retention_days`.
  - **SyslogServer** (FK SyslogConfig): `host`, `port`, `transport`.
- **NTPConfig** (1:1 Device): `enabled`, `broadcast`, `serve_lan`.
  - **NTPServer** (FK NTPConfig): `host`, `prefer`.
- **DNSResolverConfig** (1:1 Device): `mode`, `nameservers` (ordered `ArrayField`), `search_domains` (ordered `ArrayField`).

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_system_services/tests/`, one module per layer (`test_models.py`,
  `test_api.py`, `test_filtersets.py`).
- Use NetBox's base classes from `utilities.testing`: `ViewTestCases`,
  `APIViewTestCases.APIViewTestCase` (CRUD mixins), `create_test_device`. They exercise models,
  API, and filters against a **real test database** — no mocks.
- Per-device singleton configs (1:1 to Device) need a **distinct device per created object**;
  API `create_data` rows each target a fresh device.
- **Never skip a failing test** — fix the root cause.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_system_services --keepdb -v2`
  (or `pytest` with `pytest-django` + `DJANGO_SETTINGS_MODULE=netbox.settings`).
- **Coverage bar**: every model, serializer, filterset, and view has tests.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.
