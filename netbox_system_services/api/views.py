# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import (
    DnsForwardZone, DNSResolverConfig, DynamicDNSRecord, NTPConfig, NTPServer, SNMPCommunity,
    SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig, SystemTunable,
)
from .serializers import (
    DnsForwardZoneSerializer, DNSResolverConfigSerializer, DynamicDNSRecordSerializer,
    NTPConfigSerializer, NTPServerSerializer, SNMPCommunitySerializer, SNMPConfigSerializer,
    SNMPTrapTargetSerializer, SyslogConfigSerializer, SyslogServerSerializer,
    SystemConfigSerializer, SystemTunableSerializer,
)


class SystemConfigViewSet(NetBoxModelViewSet):
    queryset = SystemConfig.objects.prefetch_related("device", "tags")
    serializer_class = SystemConfigSerializer
    filterset_class = filtersets.SystemConfigFilterSet


class SNMPConfigViewSet(NetBoxModelViewSet):
    queryset = SNMPConfig.objects.prefetch_related("device", "tags")
    serializer_class = SNMPConfigSerializer
    filterset_class = filtersets.SNMPConfigFilterSet


class SNMPCommunityViewSet(NetBoxModelViewSet):
    queryset = SNMPCommunity.objects.prefetch_related("snmp_config", "tags")
    serializer_class = SNMPCommunitySerializer
    filterset_class = filtersets.SNMPCommunityFilterSet


class SNMPTrapTargetViewSet(NetBoxModelViewSet):
    queryset = SNMPTrapTarget.objects.prefetch_related("snmp_config", "tags")
    serializer_class = SNMPTrapTargetSerializer
    filterset_class = filtersets.SNMPTrapTargetFilterSet


class SyslogConfigViewSet(NetBoxModelViewSet):
    queryset = SyslogConfig.objects.prefetch_related("device", "tags")
    serializer_class = SyslogConfigSerializer
    filterset_class = filtersets.SyslogConfigFilterSet


class SyslogServerViewSet(NetBoxModelViewSet):
    queryset = SyslogServer.objects.prefetch_related("syslog_config", "tags")
    serializer_class = SyslogServerSerializer
    filterset_class = filtersets.SyslogServerFilterSet


class NTPConfigViewSet(NetBoxModelViewSet):
    queryset = NTPConfig.objects.prefetch_related("device", "tags")
    serializer_class = NTPConfigSerializer
    filterset_class = filtersets.NTPConfigFilterSet


class NTPServerViewSet(NetBoxModelViewSet):
    queryset = NTPServer.objects.prefetch_related("ntp_config", "tags")
    serializer_class = NTPServerSerializer
    filterset_class = filtersets.NTPServerFilterSet


class DNSResolverConfigViewSet(NetBoxModelViewSet):
    queryset = DNSResolverConfig.objects.prefetch_related("device", "tags")
    serializer_class = DNSResolverConfigSerializer
    filterset_class = filtersets.DNSResolverConfigFilterSet


class DnsForwardZoneViewSet(NetBoxModelViewSet):
    queryset = DnsForwardZone.objects.prefetch_related("device", "tags")
    serializer_class = DnsForwardZoneSerializer
    filterset_class = filtersets.DnsForwardZoneFilterSet


class SystemTunableViewSet(NetBoxModelViewSet):
    queryset = SystemTunable.objects.prefetch_related("device", "tags")
    serializer_class = SystemTunableSerializer
    filterset_class = filtersets.SystemTunableFilterSet


class DynamicDNSRecordViewSet(NetBoxModelViewSet):
    queryset = DynamicDNSRecord.objects.prefetch_related("device", "tags")
    serializer_class = DynamicDNSRecordSerializer
    filterset_class = filtersets.DynamicDNSRecordFilterSet
