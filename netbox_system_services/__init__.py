# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-system-services: a native NetBox source of truth for a network device's
**management-plane services** — the system identity (sysName/sysLocation/sysContact +
default gateway), SNMP (agent + communities + trap targets), syslog (severity/facility +
remote servers), NTP (client/server roles + upstream peers), and the device's **own stub
DNS resolver** (mode + nameservers + search domains).

This replaces the unstructured ``config_context`` blob we used to stash these settings in,
giving every field a real column so the ``ansible-tofu`` reconcilers read each service back
1:1. **Secret policy:** SNMP community strings and trap-target credentials are NEVER stored
here — only a logical *name*/*ref* that keys the actual secret in OpenBao. Authoritative DNS
zones are out of scope (they are netbox-dns's job); this models only the resolver the device
itself uses.
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxSystemServicesConfig(PluginConfig):
    name = "netbox_system_services"
    verbose_name = "NetBox System Services"
    description = "Native SoT for device management-plane services (SNMP, syslog, NTP, DNS resolver, system identity)"
    version = __version__
    author = "Jameson"
    base_url = "system-services"
    min_version = "4.6.0"
    max_version = "4.6.99"


config = NetBoxSystemServicesConfig
