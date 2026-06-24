# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native management-plane service models for a network device. Each feature is a per-device
singleton config (``OneToOneField`` to ``dcim.Device``) plus child rows where the data repeats
(communities, trap targets, syslog/NTP servers). Every field is a real column → these map 1:1
to the ``config_context`` keys being retired, with zero loss.

SECRET POLICY: SNMP community strings and trap-target credentials are NEVER stored here. The
community/trap models keep only a *logical name/ref* that keys the actual secret in OpenBao.
"""
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import (
    DNSForwardBackendChoices, DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices,
    SyslogFacilityChoices, SyslogSeverityChoices, SyslogTransportChoices,
)


class SystemConfig(NetBoxModel):
    """Per-device system identity: SNMP ``sysLocation``/``sysContact`` and the management
    default gateway. ``hostname`` is intentionally NOT stored — it is ``device.name``."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="system_config"
    )
    default_gateway = models.GenericIPAddressField(
        null=True, blank=True, help_text="Management-plane default gateway IP."
    )
    location = models.CharField(max_length=255, blank=True, help_text="SNMP sysLocation.")
    contact = models.CharField(max_length=255, blank=True, help_text="SNMP sysContact.")

    class Meta:
        ordering = ["device"]
        verbose_name = "System Config"

    def __str__(self):
        return f"System: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:systemconfig", args=[self.pk])


class SNMPConfig(NetBoxModel):
    """Per-device SNMP agent. ``sysContact``/``sysLocation`` are read from
    :class:`SystemConfig` (not duplicated here); this holds only the agent's own toggles."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="snmp_config"
    )
    enabled = models.BooleanField(default=True)
    listen_interface = models.CharField(
        max_length=128, blank=True, help_text="Interface the SNMP agent binds to (blank = all)."
    )

    class Meta:
        ordering = ["device"]
        verbose_name = "SNMP Config"

    def __str__(self):
        return f"SNMP: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:snmpconfig", args=[self.pk])


class SNMPCommunity(NetBoxModel):
    """An SNMP community on a device. ``name`` is a LOGICAL key, never the secret string:
    the actual community string lives in OpenBao keyed by ``name``."""

    snmp_config = models.ForeignKey(
        SNMPConfig, on_delete=models.CASCADE, related_name="communities"
    )
    name = models.CharField(
        max_length=128, help_text="Logical community key (OpenBao lookup key — NOT the secret)."
    )
    access = models.CharField(max_length=2, choices=SNMPAccessChoices, default=SNMPAccessChoices.RO)
    restricted = models.BooleanField(
        default=False, help_text="Access restricted to a source ACL / host list."
    )

    class Meta:
        ordering = ["snmp_config", "name"]
        verbose_name = "SNMP Community"
        verbose_name_plural = "SNMP Communities"
        constraints = [
            models.UniqueConstraint(
                fields=["snmp_config", "name"],
                name="netbox_system_services_snmpcommunity_unique_config_name",
            ),
        ]

    def __str__(self):
        return f"{self.snmp_config.device}: {self.name} ({self.access})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:snmpcommunity", args=[self.pk])

    def get_access_color(self):
        return SNMPAccessChoices.colors.get(self.access)


class SNMPTrapTarget(NetBoxModel):
    """An SNMP trap/notification receiver. ``community_ref`` is an OpenBao lookup key, NOT the
    secret community string."""

    snmp_config = models.ForeignKey(
        SNMPConfig, on_delete=models.CASCADE, related_name="trap_targets"
    )
    target = models.GenericIPAddressField(help_text="Trap receiver IP.")
    port = models.PositiveIntegerField(default=162)
    version = models.CharField(max_length=4, choices=SNMPVersionChoices, default=SNMPVersionChoices.V2C)
    community_ref = models.CharField(
        max_length=128, blank=True, help_text="OpenBao key for the trap community (NOT the secret)."
    )

    class Meta:
        ordering = ["snmp_config", "target", "port"]
        verbose_name = "SNMP Trap Target"

    def __str__(self):
        return f"{self.snmp_config.device}: trap → {self.target}:{self.port}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:snmptraptarget", args=[self.pk])


class SyslogConfig(NetBoxModel):
    """Per-device syslog policy: minimum severity, facility, and local retention."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="syslog_config"
    )
    severity = models.CharField(
        max_length=8, choices=SyslogSeverityChoices, default=SyslogSeverityChoices.INFO
    )
    facility = models.CharField(
        max_length=8, choices=SyslogFacilityChoices, default=SyslogFacilityChoices.USER
    )
    retention_days = models.PositiveIntegerField(default=7, help_text="Local log retention (days).")

    class Meta:
        ordering = ["device"]
        verbose_name = "Syslog Config"

    def __str__(self):
        return f"Syslog: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:syslogconfig", args=[self.pk])

    def get_severity_color(self):
        return SyslogSeverityChoices.colors.get(self.severity)


class SyslogServer(NetBoxModel):
    """A remote syslog server the device ships logs to."""

    syslog_config = models.ForeignKey(
        SyslogConfig, on_delete=models.CASCADE, related_name="servers"
    )
    host = models.GenericIPAddressField(help_text="Remote syslog server IP.")
    port = models.PositiveIntegerField(default=514)
    transport = models.CharField(
        max_length=4, choices=SyslogTransportChoices, default=SyslogTransportChoices.UDP
    )

    class Meta:
        ordering = ["syslog_config", "host", "port"]
        verbose_name = "Syslog Server"

    def __str__(self):
        return f"{self.syslog_config.device}: {self.host}:{self.port}/{self.transport}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:syslogserver", args=[self.pk])


class NTPConfig(NetBoxModel):
    """Per-device NTP roles: whether the device runs an NTP client, listens to broadcasts, and
    whether it also serves time to the LAN."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="ntp_config"
    )
    enabled = models.BooleanField(default=False, help_text="NTP client/daemon enabled.")
    broadcast = models.BooleanField(default=True, help_text="Accept broadcast/multicast time.")
    serve_lan = models.BooleanField(default=False, help_text="Also act as an NTP server for the LAN.")

    class Meta:
        ordering = ["device"]
        verbose_name = "NTP Config"

    def __str__(self):
        return f"NTP: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:ntpconfig", args=[self.pk])


class NTPServer(NetBoxModel):
    """An upstream NTP peer/server. ``host`` is a CharField (NTP peers are commonly named, e.g.
    ``pool.ntp.org`` or ``0.pool.ntp.org``, not just IPs)."""

    ntp_config = models.ForeignKey(NTPConfig, on_delete=models.CASCADE, related_name="servers")
    host = models.CharField(max_length=255, help_text="Upstream NTP server hostname or IP.")
    prefer = models.BooleanField(default=False, help_text="Mark this peer as preferred.")

    class Meta:
        ordering = ["ntp_config", "host"]
        verbose_name = "NTP Server"

    def __str__(self):
        return f"{self.ntp_config.device}: {self.host}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:ntpserver", args=[self.pk])


class DNSResolverConfig(NetBoxModel):
    """The device's OWN stub resolver — how the device resolves names for itself. This is NOT
    authoritative DNS zones (that is netbox-dns's job). ``nameservers`` and ``search_domains`` are
    ordered arrays (resolver query order is significant)."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="dns_resolver_config"
    )
    mode = models.CharField(
        max_length=8, choices=DNSResolverModeChoices, default=DNSResolverModeChoices.STATIC
    )
    nameservers = ArrayField(
        models.GenericIPAddressField(),
        default=list,
        blank=True,
        help_text="Ordered resolver IPs (query order is significant).",
    )
    search_domains = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="Ordered DNS search-domain suffixes.",
    )

    class Meta:
        ordering = ["device"]
        verbose_name = "DNS Resolver Config"

    def __str__(self):
        return f"DNS resolver: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:dnsresolverconfig", args=[self.pk])

    def get_mode_color(self):
        return DNSResolverModeChoices.colors.get(self.mode)


class DnsForwardZone(NetBoxModel):
    """A per-device conditional DNS forward zone: queries for ``domain`` are forwarded to an
    upstream resolver ``server``. Programmed into the device's local resolver daemon
    (``backend``). Distinct from :class:`DNSResolverConfig` (the device's own stub resolver) —
    this is the device acting as a forwarder for a specific zone."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="dns_forward_zones"
    )
    domain = models.CharField(max_length=255, help_text="Zone forwarded to the upstream server.")
    server = models.GenericIPAddressField(help_text="Upstream resolver IP for this zone.")
    port = models.PositiveSmallIntegerField(default=53)
    backend = models.CharField(
        max_length=16, choices=DNSForwardBackendChoices, default=DNSForwardBackendChoices.UNBOUND
    )
    tcp_upstream = models.BooleanField(
        default=False, help_text="Force TCP to the upstream resolver."
    )
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["device", "domain", "server"]
        verbose_name = "DNS Forward Zone"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "domain", "server"],
                name="netbox_system_services_dnsforwardzone_unique_device_domain_server",
            ),
        ]

    def __str__(self):
        return f"{self.device}: {self.domain} → {self.server}:{self.port}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:dnsforwardzone", args=[self.pk])

    def get_backend_color(self):
        return DNSForwardBackendChoices.colors.get(self.backend)


class SystemTunable(NetBoxModel):
    """A per-device kernel tunable (sysctl). ``name`` is the sysctl key (e.g.
    ``net.inet.ip.forwarding``); ``value`` is the literal value to set."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="system_tunables"
    )
    name = models.CharField(max_length=255, help_text="sysctl key, e.g. net.inet.ip.forwarding.")
    value = models.CharField(max_length=255, help_text="Literal sysctl value.")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["device", "name"]
        verbose_name = "System Tunable"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "name"],
                name="netbox_system_services_systemtunable_unique_device_name",
            ),
        ]

    def __str__(self):
        return f"{self.device}: {self.name}={self.value}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:systemtunable", args=[self.pk])


class DynamicDNSRecord(NetBoxModel):
    """A per-device dynamic-DNS record (ddclient): the device pushes its current public IP to a
    DNS provider for ``fqdn``. ``credential_ref`` is a LOGICAL key into OpenBao, NEVER the token
    value — the secret stays in OpenBao."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="dynamic_dns_records"
    )
    fqdn = models.CharField(max_length=255, help_text="Fully-qualified name to keep updated.")
    zone = models.CharField(max_length=255, blank=True)
    service = models.CharField(max_length=32, default="cloudflare")
    credential_ref = models.CharField(
        max_length=255, blank=True, help_text="OpenBao secret key — NEVER the token value."
    )
    check_ip_method = models.CharField(max_length=64, blank=True, default="web")
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["device", "fqdn"]
        verbose_name = "Dynamic DNS Record"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "fqdn"],
                name="netbox_system_services_dynamicdnsrecord_unique_device_fqdn",
            ),
        ]

    def __str__(self):
        return f"{self.device}: {self.fqdn} ({self.service})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:dynamicdnsrecord", args=[self.pk])
