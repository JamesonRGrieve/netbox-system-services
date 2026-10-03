# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device, Interface
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import (
    DNSForwardBackendChoices, DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices,
    SyslogFacilityChoices, SyslogSeverityChoices, SyslogTransportChoices, WakeOnLanModeChoices,
    ZramAlgorithmChoices,
)
from .models import (
    DnsForwardZone, DNSResolverConfig, DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
)


class SystemConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "fqdn", "default_gateway", name="System"),
        FieldSet("ssh_port", "ssh_password_auth", "ssh_allow_users", "ssh_host", "ssh_user",
                 "ssh_identity", name="SSH"),
        FieldSet("manage_interface_baseline", "manage_base_lan", "manage_lan",
                 "manage_timezone", "manage_reconcile", "manage_plugin_aliases",
                 name="Managed subsystems"),
        FieldSet("wan_proto", "lan_if", "vlan_trunk", "vlanif_pfstyle",
                 "openwrt_native_dsa", "openwrt_network_reload", "dhcp_engine",
                 "haproxy_setpath_separate_type", "login_banner",
                 name="Platform quirks"),
        FieldSet("location", "contact", name="SNMP identity"),
        FieldSet("config_history_count", name="Configuration history"),
    )

    class Meta:
        model = SystemConfig
        fields = ["device", "fqdn", "default_gateway", "ssh_port", "ssh_password_auth", "ssh_allow_users", "location", "contact", "tags", "ssh_host", "ssh_user", "ssh_identity", "login_banner", "manage_interface_baseline", "manage_base_lan", "manage_lan", "manage_timezone", "manage_reconcile", "manage_plugin_aliases", "wan_proto", "lan_if", "vlan_trunk", "vlanif_pfstyle", "openwrt_native_dsa", "openwrt_network_reload", "dhcp_engine", "haproxy_setpath_separate_type", "config_history_count",]


class SNMPConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (FieldSet("device", "enabled", "listen_interface", name="SNMP agent"),)

    class Meta:
        model = SNMPConfig
        fields = ["device", "enabled", "listen_interface", "tags"]


class SNMPCommunityForm(NetBoxModelForm):
    snmp_config = DynamicModelChoiceField(queryset=SNMPConfig.objects.all())

    fieldsets = (FieldSet("snmp_config", "name", "access", "restricted", name="Community"),)

    class Meta:
        model = SNMPCommunity
        fields = ["snmp_config", "name", "access", "restricted", "tags"]


class SNMPTrapTargetForm(NetBoxModelForm):
    snmp_config = DynamicModelChoiceField(queryset=SNMPConfig.objects.all())

    fieldsets = (
        FieldSet("snmp_config", "target", "port", "version", "community_ref", name="Trap target"),
    )

    class Meta:
        model = SNMPTrapTarget
        fields = ["snmp_config", "target", "port", "version", "community_ref", "tags"]


class SyslogConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "severity", "facility", "retention_days", name="Syslog policy"),
        FieldSet("filter_string", name="Filter"),
    )

    class Meta:
        model = SyslogConfig
        fields = ["device", "severity", "facility", "retention_days", "filter_string", "tags"]


class SyslogServerForm(NetBoxModelForm):
    syslog_config = DynamicModelChoiceField(queryset=SyslogConfig.objects.all())

    fieldsets = (FieldSet("syslog_config", "host", "port", "transport", name="Server"),)

    class Meta:
        model = SyslogServer
        fields = ["syslog_config", "host", "port", "transport", "tags"]


class NTPConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (FieldSet("device", "enabled", "broadcast", "serve_lan", name="NTP roles"),)

    class Meta:
        model = NTPConfig
        fields = ["device", "enabled", "broadcast", "serve_lan", "tags"]


class NTPServerForm(NetBoxModelForm):
    ntp_config = DynamicModelChoiceField(queryset=NTPConfig.objects.all())

    fieldsets = (FieldSet("ntp_config", "host", "prefer", name="Server"),)

    class Meta:
        model = NTPServer
        fields = ["ntp_config", "host", "prefer", "tags"]


class DNSResolverConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "mode", "nameservers", "search_domains", name="Resolver"),
    )

    class Meta:
        model = DNSResolverConfig
        fields = ["device", "mode", "nameservers", "search_domains", "tags"]


class DnsForwardZoneForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "domain", "server", "port", "backend", "tcp_upstream", "description", name="Forward zone"),
    )

    class Meta:
        model = DnsForwardZone
        fields = ["device", "domain", "server", "port", "backend", "tcp_upstream", "description", "tags"]


class SystemTunableForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (FieldSet("device", "name", "value", "description", name="Tunable"),)

    class Meta:
        model = SystemTunable
        fields = ["device", "name", "value", "description", "tags"]


class DynamicDNSRecordForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "fqdn", "zone", "service", "credential_ref", "check_ip_method", "enabled", name="Dynamic DNS"),
    )

    class Meta:
        model = DynamicDNSRecord
        fields = ["device", "fqdn", "zone", "service", "credential_ref", "check_ip_method", "enabled", "tags"]


class HostMemoryConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "swappiness", "swap_file_size_mb", name="Memory"),
        FieldSet("zram_percent", "zram_size_mb", "zram_algorithm", "zram_priority", name="zram"),
    )

    class Meta:
        model = HostMemoryConfig
        fields = ["device", "swappiness", "swap_file_size_mb", "zram_percent", "zram_size_mb", "zram_algorithm", "zram_priority", "tags"]


class WakeOnLanConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(), required=False, query_params={"device_id": "$device"},
    )

    fieldsets = (FieldSet("device", "enabled", "interface", "mode", "is_waker", name="Wake-on-LAN"),)

    class Meta:
        model = WakeOnLanConfig
        fields = ["device", "enabled", "interface", "mode", "is_waker", "tags"]


class WakeOnLanTargetForm(NetBoxModelForm):
    config = DynamicModelChoiceField(queryset=WakeOnLanConfig.objects.all())
    target_device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (FieldSet("config", "target_device", name="Wake-on-LAN Target"),)

    class Meta:
        model = WakeOnLanTarget
        fields = ["config", "target_device", "tags"]


class SystemConfigFilterForm(NetBoxModelFilterSetForm):
    model = SystemConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    tag = TagFilterField(SystemConfig)


class SNMPConfigFilterForm(NetBoxModelFilterSetForm):
    model = SNMPConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(SNMPConfig)


class SNMPCommunityFilterForm(NetBoxModelFilterSetForm):
    model = SNMPCommunity
    snmp_config_id = DynamicModelMultipleChoiceField(queryset=SNMPConfig.objects.all(), required=False, label="SNMP Config")
    access = forms.MultipleChoiceField(choices=SNMPAccessChoices, required=False)
    restricted = forms.NullBooleanField(required=False)
    tag = TagFilterField(SNMPCommunity)


class SNMPTrapTargetFilterForm(NetBoxModelFilterSetForm):
    model = SNMPTrapTarget
    snmp_config_id = DynamicModelMultipleChoiceField(queryset=SNMPConfig.objects.all(), required=False, label="SNMP Config")
    version = forms.MultipleChoiceField(choices=SNMPVersionChoices, required=False)
    tag = TagFilterField(SNMPTrapTarget)


class SyslogConfigFilterForm(NetBoxModelFilterSetForm):
    model = SyslogConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    severity = forms.MultipleChoiceField(choices=SyslogSeverityChoices, required=False)
    facility = forms.MultipleChoiceField(choices=SyslogFacilityChoices, required=False)
    tag = TagFilterField(SyslogConfig)


class SyslogServerFilterForm(NetBoxModelFilterSetForm):
    model = SyslogServer
    syslog_config_id = DynamicModelMultipleChoiceField(queryset=SyslogConfig.objects.all(), required=False, label="Syslog Config")
    transport = forms.MultipleChoiceField(choices=SyslogTransportChoices, required=False)
    tag = TagFilterField(SyslogServer)


class NTPConfigFilterForm(NetBoxModelFilterSetForm):
    model = NTPConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    enabled = forms.NullBooleanField(required=False)
    broadcast = forms.NullBooleanField(required=False)
    serve_lan = forms.NullBooleanField(required=False)
    tag = TagFilterField(NTPConfig)


class NTPServerFilterForm(NetBoxModelFilterSetForm):
    model = NTPServer
    ntp_config_id = DynamicModelMultipleChoiceField(queryset=NTPConfig.objects.all(), required=False, label="NTP Config")
    prefer = forms.NullBooleanField(required=False)
    tag = TagFilterField(NTPServer)


class DNSResolverConfigFilterForm(NetBoxModelFilterSetForm):
    model = DNSResolverConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    mode = forms.MultipleChoiceField(choices=DNSResolverModeChoices, required=False)
    tag = TagFilterField(DNSResolverConfig)


class DnsForwardZoneFilterForm(NetBoxModelFilterSetForm):
    model = DnsForwardZone
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    backend = forms.MultipleChoiceField(choices=DNSForwardBackendChoices, required=False)
    tcp_upstream = forms.NullBooleanField(required=False)
    tag = TagFilterField(DnsForwardZone)


class SystemTunableFilterForm(NetBoxModelFilterSetForm):
    model = SystemTunable
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    tag = TagFilterField(SystemTunable)


class DynamicDNSRecordFilterForm(NetBoxModelFilterSetForm):
    model = DynamicDNSRecord
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(DynamicDNSRecord)


class HostMemoryConfigFilterForm(NetBoxModelFilterSetForm):
    model = HostMemoryConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    zram_algorithm = forms.MultipleChoiceField(choices=ZramAlgorithmChoices, required=False)
    tag = TagFilterField(HostMemoryConfig)


class WakeOnLanConfigFilterForm(NetBoxModelFilterSetForm):
    model = WakeOnLanConfig
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    mode = forms.MultipleChoiceField(choices=WakeOnLanModeChoices, required=False)
    enabled = forms.NullBooleanField(required=False)
    is_waker = forms.NullBooleanField(required=False)
    tag = TagFilterField(WakeOnLanConfig)


class WakeOnLanTargetFilterForm(NetBoxModelFilterSetForm):
    model = WakeOnLanTarget
    config_id = DynamicModelMultipleChoiceField(queryset=WakeOnLanConfig.objects.all(), required=False, label="WoL Config")
    target_device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Target Device")
    tag = TagFilterField(WakeOnLanTarget)
