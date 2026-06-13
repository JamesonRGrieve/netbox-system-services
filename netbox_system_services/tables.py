# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    DNSResolverConfig, NTPConfig, NTPServer, SNMPCommunity, SNMPConfig, SNMPTrapTarget,
    SyslogConfig, SyslogServer, SystemConfig,
)


class SystemConfigTable(NetBoxTable):
    device = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_system_services:systemconfig_list")

    class Meta(NetBoxTable.Meta):
        model = SystemConfig
        fields = ("pk", "id", "device", "default_gateway", "location", "contact", "tags", "created", "last_updated")
        default_columns = ("device", "default_gateway", "location", "contact")


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
        fields = ("pk", "id", "device", "severity", "facility", "retention_days", "tags", "created", "last_updated")
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
