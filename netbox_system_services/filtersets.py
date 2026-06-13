# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from dcim.models import Device
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .choices import (
    DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices, SyslogFacilityChoices,
    SyslogSeverityChoices, SyslogTransportChoices,
)
from .models import (
    DNSResolverConfig, NTPConfig, NTPServer, SNMPCommunity, SNMPConfig, SNMPTrapTarget,
    SyslogConfig, SyslogServer, SystemConfig,
)

# Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields,
# so `?device_id=` would be silently ignored. NetBox convention is `<fk>_id` (by PK) +
# `<fk>` (by natural key/name).


class _DeviceFilterMixin(NetBoxModelFilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device", queryset=Device.objects.all(), label="Device (ID)"
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name", to_field_name="name", queryset=Device.objects.all(),
        label="Device (name)",
    )

    class Meta:
        abstract = True


class SystemConfigFilterSet(_DeviceFilterMixin):
    class Meta:
        model = SystemConfig
        fields = ["id", "default_gateway", "location", "contact"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(device__name__icontains=value) | Q(location__icontains=value)
            | Q(contact__icontains=value)
        )


class SNMPConfigFilterSet(_DeviceFilterMixin):
    class Meta:
        model = SNMPConfig
        fields = ["id", "enabled", "listen_interface"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(device__name__icontains=value) | Q(listen_interface__icontains=value)
        )


class SNMPCommunityFilterSet(NetBoxModelFilterSet):
    snmp_config_id = django_filters.ModelMultipleChoiceFilter(
        field_name="snmp_config", queryset=SNMPConfig.objects.all(), label="SNMP Config (ID)"
    )
    access = django_filters.MultipleChoiceFilter(choices=SNMPAccessChoices)

    class Meta:
        model = SNMPCommunity
        fields = ["id", "name", "restricted"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))


class SNMPTrapTargetFilterSet(NetBoxModelFilterSet):
    snmp_config_id = django_filters.ModelMultipleChoiceFilter(
        field_name="snmp_config", queryset=SNMPConfig.objects.all(), label="SNMP Config (ID)"
    )
    version = django_filters.MultipleChoiceFilter(choices=SNMPVersionChoices)

    class Meta:
        model = SNMPTrapTarget
        fields = ["id", "target", "port", "community_ref"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(target__icontains=value) | Q(community_ref__icontains=value))


class SyslogConfigFilterSet(_DeviceFilterMixin):
    severity = django_filters.MultipleChoiceFilter(choices=SyslogSeverityChoices)
    facility = django_filters.MultipleChoiceFilter(choices=SyslogFacilityChoices)

    class Meta:
        model = SyslogConfig
        fields = ["id", "retention_days"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(device__name__icontains=value))


class SyslogServerFilterSet(NetBoxModelFilterSet):
    syslog_config_id = django_filters.ModelMultipleChoiceFilter(
        field_name="syslog_config", queryset=SyslogConfig.objects.all(), label="Syslog Config (ID)"
    )
    transport = django_filters.MultipleChoiceFilter(choices=SyslogTransportChoices)

    class Meta:
        model = SyslogServer
        fields = ["id", "host", "port"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(host__icontains=value))


class NTPConfigFilterSet(_DeviceFilterMixin):
    class Meta:
        model = NTPConfig
        fields = ["id", "enabled", "broadcast", "serve_lan"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(device__name__icontains=value))


class NTPServerFilterSet(NetBoxModelFilterSet):
    ntp_config_id = django_filters.ModelMultipleChoiceFilter(
        field_name="ntp_config", queryset=NTPConfig.objects.all(), label="NTP Config (ID)"
    )

    class Meta:
        model = NTPServer
        fields = ["id", "host", "prefer"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(host__icontains=value))


class DNSResolverConfigFilterSet(_DeviceFilterMixin):
    mode = django_filters.MultipleChoiceFilter(choices=DNSResolverModeChoices)

    class Meta:
        model = DNSResolverConfig
        fields = ["id"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(device__name__icontains=value))
