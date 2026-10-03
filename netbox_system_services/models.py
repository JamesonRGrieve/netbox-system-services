# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native management-plane service models for a network device. Each feature is a per-device
singleton config (``OneToOneField`` to ``dcim.Device``) plus child rows where the data repeats
(communities, trap targets, syslog/NTP servers). Every field is a real column → these map 1:1
to the ``config_context`` keys being retired, with zero loss.

SECRET POLICY: SNMP community strings and trap-target credentials are NEVER stored here. The
community/trap models keep only a *logical name/ref* that keys the actual secret in OpenBao.
"""
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import (
    DNSForwardBackendChoices, DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices,
    SyslogFacilityChoices, SyslogSeverityChoices, SyslogTransportChoices, WakeOnLanModeChoices,
    ZramAlgorithmChoices,
)


class SystemConfig(NetBoxModel):
    """Per-device system identity and management-plane SSH/network config."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="system_config"
    )
    fqdn = models.CharField(
        max_length=255, blank=True,
        help_text="Fully qualified domain name. The leftmost label is the system hostname; "
                  "the remainder is the domain. When blank, device.name is used as hostname "
                  "with no domain. Decoupled from device.name so Bao secret paths "
                  "(keyed on device.name) remain stable."
    )
    default_gateway = models.GenericIPAddressField(
        null=True, blank=True, help_text="Management-plane default gateway IP."
    )
    location = models.CharField(max_length=255, blank=True, help_text="SNMP sysLocation.")
    contact = models.CharField(max_length=255, blank=True, help_text="SNMP sysContact.")
    ssh_port = models.PositiveIntegerField(
        default=22, help_text="SSHd listen port."
    )
    ssh_password_auth = models.BooleanField(
        default=True, help_text="Allow SSH password authentication."
    )
    ssh_allow_users = ArrayField(
        models.CharField(max_length=128), default=list, blank=True,
        help_text="SSHd AllowUsers list (empty = unrestricted)."
    )
    ssh_proxy_host = models.CharField(
        max_length=255, blank=True, help_text="SSH ProxyJump host (empty = direct connection)."
    )
    ssh_proxy_port = models.PositiveIntegerField(
        default=22, help_text="SSH ProxyJump port."
    )
    ssh_proxy_user = models.CharField(
        max_length=128, blank=True, help_text="SSH ProxyJump user."
    )
    ssh_proxy_identity = models.CharField(
        max_length=255, blank=True, help_text="OpenBao KV path for the ProxyJump private key."
    )

    # --- Management reach (supersedes the ssh_host/ssh_user/ssh_identity custom fields) ---
    ssh_host = models.CharField(
        max_length=255, blank=True,
        help_text="Address SSHd is reached at, when that is NOT the device's primary_ip4. "
                  "OPNsense binds sshd to a different interface than its API, so the two differ. "
                  "Blank = use primary_ip4."
    )
    ssh_user = models.CharField(
        max_length=128, blank=True, help_text="SSH user for management. Blank = root."
    )
    ssh_identity = models.CharField(
        max_length=255, blank=True,
        help_text="OpenBao KV path for this device's own SSH private key. A reference, never the "
                  "key. Blank = the shared runner identity."
    )
    login_banner = models.TextField(
        blank=True, help_text="Pre-login banner text (/etc/issue.net or the platform equivalent)."
    )

    # --- Subsystem management toggles: what the pipeline is allowed to rewrite ---
    # Each one exists because an ADOPTED device must not have that subsystem reset to the
    # fleet baseline on its first converge. They are opt-OUT (default true) except where
    # enabling would rewrite a live box, which is why manage_interface_baseline defaults false.
    manage_interface_baseline = models.BooleanField(
        default=False,
        help_text="Rewrite the WAN/MGMT/LAN interface baseline. FALSE for any already-deployed "
                  "multi-VLAN box: enabling it re-runs a 3-NIC bringup over live assignments."
    )
    manage_base_lan = models.BooleanField(
        default=False, help_text="Manage the untagged base LAN section on the trunk parent."
    )
    manage_lan = models.BooleanField(default=True, help_text="Manage LAN interface config.")
    manage_timezone = models.BooleanField(default=True, help_text="Manage the system timezone.")
    manage_reconcile = models.BooleanField(
        default=True,
        help_text="Emit the unconditional per-converge service reload. FALSE where the mgmt user "
                  "cannot run it (e.g. an ubus login lacking the file.exec ACL); core CRUD still "
                  "reloads on write."
    )
    manage_plugin_aliases = models.BooleanField(
        default=True, help_text="Manage firewall aliases owned by the plugin layer."
    )

    # --- Platform quirks ---
    wan_proto = models.CharField(
        max_length=32, blank=True, help_text="WAN addressing protocol (dhcp, static, pppoe...)."
    )
    lan_if = models.CharField(
        max_length=64, blank=True, help_text="Physical interface carrying the LAN role."
    )
    vlan_trunk = models.CharField(
        max_length=64, blank=True,
        help_text="Physical parent the VLAN sub-interfaces trunk over (e.g. re0)."
    )
    vlanif_pfstyle = models.BooleanField(
        default=False,
        help_text="Name VLAN interfaces the pfSense way rather than the OPNsense way."
    )
    openwrt_native_dsa = models.BooleanField(
        default=False,
        help_text="Device uses the native DSA bridge-VLAN model rather than legacy swconfig."
    )
    openwrt_network_reload = models.BooleanField(
        default=True,
        help_text="Allow a full `network` reload. A reload re-applies any reset='1' stanza, so it "
                  "can bounce the whole switch — off for boxes where that is unacceptable."
    )
    dhcp_engine = models.CharField(
        max_length=32, blank=True, help_text="DHCP server implementation (dnsmasq, kea, isc)."
    )
    haproxy_setpath_separate_type = models.BooleanField(
        default=False,
        help_text="This HAProxy build needs set-path and set-header as SEPARATE actions rather "
                  "than one combined action."
    )

    # --- Configuration history ---
    config_history_count = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)],
        help_text="Configuration revisions the device keeps (OPNsense <system><backupcount>). "
                  "Blank = leave the device default (100 on OPNsense). 0 is rejected: OPNsense "
                  "would delete every saved revision."
    )

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
    filter_string = models.TextField(
        blank=True, help_text="Syslog filter expression (platform-specific, e.g. rsyslog property-based filter)."
    )

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


class HostMemoryConfig(NetBoxModel):
    """Per-device host memory management: kernel ``vm.swappiness``, a traditional ``/swapfile``,
    and a compressed ``zram`` swap device. Every config field is nullable/blank — an unset field
    means *unmanaged* (the subset semantics the sibling configs use). Maps 1:1 to the memory
    attributes of the ``proxmox_host_config`` tofu resource. ``zram_percent`` and ``zram_size_mb``
    are mutually exclusive (size expressed either relative to RAM or absolute, never both)."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="host_memory_config"
    )
    swappiness = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(200)],
        help_text="vm.swappiness (0–200); unset = unmanaged.",
    )
    swap_file_size_mb = models.PositiveIntegerField(
        null=True, blank=True, help_text="Traditional /swapfile size in MiB (0 = removed)."
    )
    zram_percent = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(100)],
        help_text="zram size as a percentage of RAM (mutually exclusive with zram_size_mb).",
    )
    zram_size_mb = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Absolute zram size in MiB (mutually exclusive with zram_percent).",
    )
    zram_algorithm = models.CharField(
        max_length=20, blank=True, choices=ZramAlgorithmChoices, help_text="zram compression algorithm."
    )
    zram_priority = models.SmallIntegerField(
        null=True, blank=True, help_text="zram swap priority (provider default 100 when unset)."
    )

    class Meta:
        ordering = ["device"]
        verbose_name = "Host Memory Config"

    def __str__(self):
        return f"Host Memory: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:hostmemoryconfig", args=[self.pk])

    def clean(self):
        super().clean()
        if self.zram_percent is not None and self.zram_size_mb is not None:
            raise ValidationError(
                "zram_percent and zram_size_mb are mutually exclusive — set at most one."
            )


class WakeOnLanConfig(NetBoxModel):
    """Per-device Wake-on-LAN posture with two independent roles. (1) *Be woken*: this host's NIC
    is armed to accept magic packets — ``enabled`` + the wake ``interface`` + the ethtool ``mode``;
    the magic-packet MAC target is read LIVE from ``interface`` and is NEVER stored here. (2) *Waker*:
    ``is_waker`` marks this host as one that SENDS magic packets to wake others, whose targets hang
    off it as :class:`WakeOnLanTarget` child rows."""

    device = models.OneToOneField(
        "dcim.Device", on_delete=models.CASCADE, related_name="wake_on_lan_config"
    )
    enabled = models.BooleanField(default=False, help_text="WoL armed on this host's NIC (be-woken).")
    interface = models.ForeignKey(
        "dcim.Interface", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
        help_text="Wake NIC; its MAC is the magic-packet target (read live, never stored here).",
    )
    mode = models.CharField(
        max_length=10, choices=WakeOnLanModeChoices, default=WakeOnLanModeChoices.MAGIC,
        help_text="ethtool wol mode.",
    )
    is_waker = models.BooleanField(
        default=False, help_text="This host sends magic packets to wake others."
    )

    class Meta:
        ordering = ["device"]
        verbose_name = "Wake-on-LAN Config"

    def __str__(self):
        return f"WoL: {self.device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:wakeonlanconfig", args=[self.pk])

    def clean(self):
        super().clean()
        if self.interface is not None and self.interface.device_id != self.device_id:
            raise ValidationError("The wake interface must belong to this device.")


class WakeOnLanTarget(NetBoxModel):
    """A host that a waker (:class:`WakeOnLanConfig` with ``is_waker=True``) wakes. Child row hanging
    off the waker's config; ``target_device`` is the woken host (its wake MAC is read from that
    device's own :class:`WakeOnLanConfig` interface, never duplicated here)."""

    config = models.ForeignKey(
        WakeOnLanConfig, on_delete=models.CASCADE, related_name="targets"
    )
    target_device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="+"
    )

    class Meta:
        ordering = ["config", "target_device"]
        verbose_name = "Wake-on-LAN Target"
        constraints = [
            models.UniqueConstraint(
                fields=["config", "target_device"],
                name="netbox_system_services_wakeonlantarget_unique_config_target",
            ),
        ]

    def __str__(self):
        return f"{self.config.device} -> {self.target_device}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:wakeonlantarget", args=[self.pk])


class DnsHostAlias(NetBoxModel):
    """A per-device DNS host override / alias (Unbound host_override or dnsmasq address=)."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="dns_host_aliases"
    )
    hostname = models.CharField(max_length=255, help_text="FQDN or short hostname to override.")
    target = models.GenericIPAddressField(help_text="IP address the hostname resolves to.")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["device", "hostname"]
        verbose_name = "DNS Host Alias"
        verbose_name_plural = "DNS Host Aliases"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "hostname"],
                name="netbox_system_services_dnshostalias_unique_device_hostname",
            ),
        ]

    def __str__(self):
        return f"{self.device}: {self.hostname} -> {self.target}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:dnshostalias", args=[self.pk])


class DnsmasqHost(NetBoxModel):
    """A per-device dnsmasq static host entry (--host-record)."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="dnsmasq_hosts"
    )
    hostname = models.CharField(max_length=255, help_text="Hostname for the dnsmasq host record.")
    ip_address = models.GenericIPAddressField(help_text="IP address for the host record.")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["device", "hostname"]
        verbose_name = "Dnsmasq Host"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "hostname"],
                name="netbox_system_services_dnsmasqhost_unique_device_hostname",
            ),
        ]

    def __str__(self):
        return f"{self.device}: {self.hostname} -> {self.ip_address}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:dnsmasqhost", args=[self.pk])


class DeviceCLILine(NetBoxModel):
    """A per-device raw CLI configuration line (platform-specific escape hatch)."""

    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, related_name="cli_lines"
    )
    line = models.TextField(help_text="Raw CLI line to include in the device config.")
    weight = models.PositiveIntegerField(default=100, help_text="Ordering weight (lower = earlier).")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["device", "weight"]
        verbose_name = "Device CLI Line"

    def __str__(self):
        return f"{self.device}: {self.line[:60]}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_system_services:devicecliline", args=[self.pk])
