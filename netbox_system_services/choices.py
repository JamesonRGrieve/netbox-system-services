# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the management-plane service models. Values match the on-device tokens
(SNMP access, syslog severity/facility, syslog/NTP transport, DNS resolver mode) verbatim."""
from utilities.choices import ChoiceSet


class SNMPAccessChoices(ChoiceSet):
    """SNMP community access level."""
    RO = "ro"
    RW = "rw"
    CHOICES = [(RO, "Read-only", "green"), (RW, "Read-write", "orange")]


class SNMPVersionChoices(ChoiceSet):
    """SNMP protocol version used to send traps."""
    V1 = "v1"
    V2C = "v2c"
    CHOICES = [(V1, "v1"), (V2C, "v2c")]


class SyslogSeverityChoices(ChoiceSet):
    """Minimum severity logged (syslog RFC 5424 keyword subset we surface)."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CHOICES = [
        (DEBUG, "Debug", "gray"), (INFO, "Info", "blue"),
        (WARNING, "Warning", "orange"), (ERROR, "Error", "red"),
    ]


class SyslogFacilityChoices(ChoiceSet):
    """syslog facility (RFC 5424); the local0..local7 range is the locally-assigned set."""
    USER = "user"
    LOCAL0 = "local0"
    LOCAL1 = "local1"
    LOCAL2 = "local2"
    LOCAL3 = "local3"
    LOCAL4 = "local4"
    LOCAL5 = "local5"
    LOCAL6 = "local6"
    LOCAL7 = "local7"
    CHOICES = [
        (USER, "user"), (LOCAL0, "local0"), (LOCAL1, "local1"), (LOCAL2, "local2"),
        (LOCAL3, "local3"), (LOCAL4, "local4"), (LOCAL5, "local5"), (LOCAL6, "local6"),
        (LOCAL7, "local7"),
    ]


class SyslogTransportChoices(ChoiceSet):
    """Transport for shipping logs to a remote syslog server."""
    UDP = "udp"
    TCP = "tcp"
    TLS = "tls"
    CHOICES = [(UDP, "UDP"), (TCP, "TCP"), (TLS, "TLS")]


class DNSResolverModeChoices(ChoiceSet):
    """How the device's own stub resolver gets its nameservers."""
    STATIC = "static"
    DHCP = "dhcp"
    CHOICES = [(STATIC, "Static", "blue"), (DHCP, "DHCP", "green")]


class DNSForwardBackendChoices(ChoiceSet):
    """Resolver daemon a conditional forward zone is programmed into."""
    UNBOUND = "unbound"
    DNSMASQ = "dnsmasq"
    CHOICES = [(UNBOUND, "Unbound", "blue"), (DNSMASQ, "Dnsmasq", "green")]


class WakeOnLanModeChoices(ChoiceSet):
    """ethtool Wake-on-LAN mode tokens (the ``wol`` flags a NIC can be armed with)."""
    MAGIC = "g"
    ARP = "a"
    UNICAST = "u"
    MULTICAST = "m"
    BROADCAST = "b"
    PHY = "p"
    DISABLE = "d"
    CHOICES = [
        (MAGIC, "Magic packet (g)"), (ARP, "ARP (a)"), (UNICAST, "Unicast (u)"),
        (MULTICAST, "Multicast (m)"), (BROADCAST, "Broadcast (b)"), (PHY, "PHY activity (p)"),
        (DISABLE, "Disabled (d)"),
    ]


class ZramAlgorithmChoices(ChoiceSet):
    """Compression algorithm for a zram swap device (values match the on-disk zram tokens)."""
    ZSTD = "zstd"
    LZ4 = "lz4"
    LZO = "lzo"
    LZO_RLE = "lzo-rle"
    LZ4HC = "lz4hc"
    DEFLATE_842 = "842"
    CHOICES = [
        (ZSTD, "Zstd"), (LZ4, "LZ4"), (LZO, "LZO"),
        (LZO_RLE, "LZO-RLE"), (LZ4HC, "LZ4HC"), (DEFLATE_842, "842"),
    ]
