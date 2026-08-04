# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    DnsForwardZone, DNSResolverConfig, DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
)


class SystemConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:systemconfig_list")

    class Meta(NetBoxTable.Meta):
        model = SystemConfig
        fields = ("pk", "id", "device", "default_gateway", "ssh_port", "ssh_password_auth", "location", "contact", "tags", "created", "last_updated")
        default_columns = ("device", "default_gateway", "ssh_port", "location", "contact")


class SNMPConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:snmpconfig_list")

    class Meta(NetBoxTable.Meta):
        model = SNMPConfig
        fields = ("pk", "id", "device", "enabled", "listen_interface", "tags", "created", "last_updated")
        default_columns = ("device", "enabled", "listen_interface")


class SNMPCommunityTable(NetBoxTable):
    snmp_config = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    access = columns.ChoiceFieldColumn()
    restricted = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:snmpcommunity_list")

    class Meta(NetBoxTable.Meta):
        model = SNMPCommunity
        fields = ("pk", "id", "snmp_config", "name", "access", "restricted", "tags", "created", "last_updated")
        default_columns = ("snmp_config", "name", "access", "restricted")


class SNMPTrapTargetTable(NetBoxTable):
    snmp_config = tables.Column(linkify=True)
    target = tables.Column(linkify=True)
    version = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:snmptraptarget_list")

    class Meta(NetBoxTable.Meta):
        model = SNMPTrapTarget
        fields = ("pk", "id", "snmp_config", "target", "port", "version", "community_ref", "tags", "created", "last_updated")
        default_columns = ("snmp_config", "target", "port", "version", "community_ref")


class SyslogConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    severity = columns.ChoiceFieldColumn()
    facility = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:syslogconfig_list")

    class Meta(NetBoxTable.Meta):
        model = SyslogConfig
        fields = ("pk", "id", "device", "severity", "facility", "retention_days", "filter_string", "tags", "created", "last_updated")
        default_columns = ("device", "severity", "facility", "retention_days")


class SyslogServerTable(NetBoxTable):
    syslog_config = tables.Column(linkify=True)
    host = tables.Column(linkify=True)
    transport = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:syslogserver_list")

    class Meta(NetBoxTable.Meta):
        model = SyslogServer
        fields = ("pk", "id", "syslog_config", "host", "port", "transport", "tags", "created", "last_updated")
        default_columns = ("syslog_config", "host", "port", "transport")


class NTPConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    broadcast = columns.BooleanColumn()
    serve_lan = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:ntpconfig_list")

    class Meta(NetBoxTable.Meta):
        model = NTPConfig
        fields = ("pk", "id", "device", "enabled", "broadcast", "serve_lan", "tags", "created", "last_updated")
        default_columns = ("device", "enabled", "broadcast", "serve_lan")


class NTPServerTable(NetBoxTable):
    ntp_config = tables.Column(linkify=True)
    host = tables.Column(linkify=True)
    prefer = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:ntpserver_list")

    class Meta(NetBoxTable.Meta):
        model = NTPServer
        fields = ("pk", "id", "ntp_config", "host", "prefer", "tags", "created", "last_updated")
        default_columns = ("ntp_config", "host", "prefer")


class DNSResolverConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    mode = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:dnsresolverconfig_list")

    class Meta(NetBoxTable.Meta):
        model = DNSResolverConfig
        fields = ("pk", "id", "device", "mode", "nameservers", "search_domains", "tags", "created", "last_updated")
        default_columns = ("device", "mode", "nameservers", "search_domains")


class DnsForwardZoneTable(NetBoxTable):
    device = tables.Column(linkify=True)
    domain = tables.Column(linkify=True)
    backend = columns.ChoiceFieldColumn()
    tcp_upstream = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:dnsforwardzone_list")

    class Meta(NetBoxTable.Meta):
        model = DnsForwardZone
        fields = ("pk", "id", "device", "domain", "server", "port", "backend", "tcp_upstream", "description", "tags", "created", "last_updated")
        default_columns = ("device", "domain", "server", "port", "backend")


class SystemTunableTable(NetBoxTable):
    device = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:systemtunable_list")

    class Meta(NetBoxTable.Meta):
        model = SystemTunable
        fields = ("pk", "id", "device", "name", "value", "description", "tags", "created", "last_updated")
        default_columns = ("device", "name", "value")


class DynamicDNSRecordTable(NetBoxTable):
    device = tables.Column(linkify=True)
    fqdn = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:dynamicdnsrecord_list")

    class Meta(NetBoxTable.Meta):
        model = DynamicDNSRecord
        fields = ("pk", "id", "device", "fqdn", "zone", "service", "credential_ref", "check_ip_method", "enabled", "tags", "created", "last_updated")
        default_columns = ("device", "fqdn", "service", "enabled")


class HostMemoryConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    zram_algorithm = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:hostmemoryconfig_list")

    class Meta(NetBoxTable.Meta):
        model = HostMemoryConfig
        fields = ("pk", "id", "device", "swappiness", "swap_file_size_mb", "zram_percent", "zram_size_mb", "zram_algorithm", "zram_priority", "tags", "created", "last_updated")
        default_columns = ("device", "swappiness", "swap_file_size_mb", "zram_percent", "zram_algorithm")


class WakeOnLanConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    interface = tables.Column(linkify=True)
    enabled = columns.BooleanColumn()
    mode = columns.ChoiceFieldColumn()
    is_waker = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:wakeonlanconfig_list")

    class Meta(NetBoxTable.Meta):
        model = WakeOnLanConfig
        fields = ("pk", "id", "device", "enabled", "interface", "mode", "is_waker", "tags", "created", "last_updated")
        default_columns = ("device", "enabled", "interface", "mode", "is_waker")


class WakeOnLanTargetTable(NetBoxTable):
    config = tables.Column(linkify=True)
    target_device = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:wakeonlantarget_list")

    class Meta(NetBoxTable.Meta):
        model = WakeOnLanTarget
        fields = ("pk", "id", "config", "target_device", "tags", "created", "last_updated")
        default_columns = ("config", "target_device")
