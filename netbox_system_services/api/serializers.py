# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer, InterfaceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from ..models import (
    DeviceCLILine, DnsForwardZone, DnsHostAlias, DnsmasqHost, DNSResolverConfig,
    DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
)


class SystemConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:systemconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = SystemConfig
        fields = [
            "id", "url", "display", "device", "fqdn", "default_gateway", "location", "contact",
            "ssh_port", "ssh_password_auth", "ssh_allow_users",
            "ssh_proxy_host", "ssh_proxy_port", "ssh_proxy_user", "ssh_proxy_identity",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device"]


class SNMPConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:snmpconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = SNMPConfig
        fields = [
            "id", "url", "display", "device", "enabled", "listen_interface",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "enabled"]


class SNMPCommunitySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:snmpcommunity-detail")
    snmp_config = SNMPConfigSerializer(nested=True)

    class Meta:
        model = SNMPCommunity
        fields = [
            "id", "url", "display", "snmp_config", "name", "access", "restricted",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "access"]


class SNMPTrapTargetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:snmptraptarget-detail")
    snmp_config = SNMPConfigSerializer(nested=True)

    class Meta:
        model = SNMPTrapTarget
        fields = [
            "id", "url", "display", "snmp_config", "target", "port", "version", "community_ref",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "target", "port"]


class SyslogConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:syslogconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = SyslogConfig
        fields = [
            "id", "url", "display", "device", "severity", "facility", "retention_days",
            "filter_string", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "severity"]


class SyslogServerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:syslogserver-detail")
    syslog_config = SyslogConfigSerializer(nested=True)

    class Meta:
        model = SyslogServer
        fields = [
            "id", "url", "display", "syslog_config", "host", "port", "transport",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "host", "port"]


class NTPConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:ntpconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = NTPConfig
        fields = [
            "id", "url", "display", "device", "enabled", "broadcast", "serve_lan",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "enabled"]


class NTPServerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:ntpserver-detail")
    ntp_config = NTPConfigSerializer(nested=True)

    class Meta:
        model = NTPServer
        fields = [
            "id", "url", "display", "ntp_config", "host", "prefer",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "host", "prefer"]


class DNSResolverConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:dnsresolverconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DNSResolverConfig
        fields = [
            "id", "url", "display", "device", "mode", "nameservers", "search_domains",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "mode"]


class DnsForwardZoneSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:dnsforwardzone-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DnsForwardZone
        fields = [
            "id", "url", "display", "device", "domain", "server", "port", "backend",
            "tcp_upstream", "description", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "domain", "server"]


class SystemTunableSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:systemtunable-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = SystemTunable
        fields = [
            "id", "url", "display", "device", "name", "value", "description",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "name", "value"]


class DynamicDNSRecordSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:dynamicdnsrecord-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DynamicDNSRecord
        fields = [
            "id", "url", "display", "device", "fqdn", "zone", "service", "credential_ref",
            "check_ip_method", "enabled", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "fqdn", "service"]


class HostMemoryConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:hostmemoryconfig-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = HostMemoryConfig
        fields = [
            "id", "url", "display", "device", "swappiness", "swap_file_size_mb", "zram_percent",
            "zram_size_mb", "zram_algorithm", "zram_priority",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device"]


class WakeOnLanConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:wakeonlanconfig-detail")
    device = DeviceSerializer(nested=True)
    interface = InterfaceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = WakeOnLanConfig
        fields = [
            "id", "url", "display", "device", "enabled", "interface", "mode", "is_waker",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "is_waker"]


class WakeOnLanTargetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:wakeonlantarget-detail")
    config = WakeOnLanConfigSerializer(nested=True)
    target_device = DeviceSerializer(nested=True)

    class Meta:
        model = WakeOnLanTarget
        fields = [
            "id", "url", "display", "config", "target_device",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "config", "target_device"]


class DnsHostAliasSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:dnshostalias-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DnsHostAlias
        fields = [
            "id", "url", "display", "device", "hostname", "target", "description",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "hostname", "target"]


class DnsmasqHostSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:dnsmasqhost-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DnsmasqHost
        fields = [
            "id", "url", "display", "device", "hostname", "ip_address", "description",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "hostname", "ip_address"]


class DeviceCLILineSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_system_services-api:devicecliline-detail")
    device = DeviceSerializer(nested=True)

    class Meta:
        model = DeviceCLILine
        fields = [
            "id", "url", "display", "device", "line", "weight", "description",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "device", "weight"]
