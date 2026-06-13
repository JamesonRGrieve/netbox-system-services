# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import (
    DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices, SyslogFacilityChoices,
    SyslogSeverityChoices, SyslogTransportChoices,
)
from .models import (
    DNSResolverConfig, NTPConfig, NTPServer, SNMPCommunity, SNMPConfig, SNMPTrapTarget,
    SyslogConfig, SyslogServer, SystemConfig,
)


class SystemConfigForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())

    fieldsets = (
        FieldSet("device", "default_gateway", name="System"),
        FieldSet("location", "contact", name="SNMP identity"),
    )

    class Meta:
        model = SystemConfig
        fields = ["device", "default_gateway", "location", "contact", "tags"]


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
    )

    class Meta:
        model = SyslogConfig
        fields = ["device", "severity", "facility", "retention_days", "tags"]


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
