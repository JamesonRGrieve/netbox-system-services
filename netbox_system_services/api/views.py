# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import (
    DeviceCLILine, DnsForwardZone, DnsHostAlias, DnsmasqHost, DNSResolverConfig,
    DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
)
from .serializers import (
    DeviceCLILineSerializer, DnsForwardZoneSerializer, DnsHostAliasSerializer,
    DnsmasqHostSerializer, DNSResolverConfigSerializer, DynamicDNSRecordSerializer,
    HostMemoryConfigSerializer, NTPConfigSerializer, NTPServerSerializer, SNMPCommunitySerializer,
    SNMPConfigSerializer, SNMPTrapTargetSerializer, SyslogConfigSerializer, SyslogServerSerializer,
    SystemConfigSerializer, SystemTunableSerializer, WakeOnLanConfigSerializer,
    WakeOnLanTargetSerializer,
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


class HostMemoryConfigViewSet(NetBoxModelViewSet):
    queryset = HostMemoryConfig.objects.prefetch_related("device", "tags")
    serializer_class = HostMemoryConfigSerializer
    filterset_class = filtersets.HostMemoryConfigFilterSet


class WakeOnLanConfigViewSet(NetBoxModelViewSet):
    queryset = WakeOnLanConfig.objects.prefetch_related("device", "interface", "tags")
    serializer_class = WakeOnLanConfigSerializer
    filterset_class = filtersets.WakeOnLanConfigFilterSet


class WakeOnLanTargetViewSet(NetBoxModelViewSet):
    queryset = WakeOnLanTarget.objects.prefetch_related("config", "target_device", "tags")
    serializer_class = WakeOnLanTargetSerializer
    filterset_class = filtersets.WakeOnLanTargetFilterSet


class DnsHostAliasViewSet(NetBoxModelViewSet):
    queryset = DnsHostAlias.objects.prefetch_related("device", "tags")
    serializer_class = DnsHostAliasSerializer
    filterset_class = filtersets.DnsHostAliasFilterSet


class DnsmasqHostViewSet(NetBoxModelViewSet):
    queryset = DnsmasqHost.objects.prefetch_related("device", "tags")
    serializer_class = DnsmasqHostSerializer
    filterset_class = filtersets.DnsmasqHostFilterSet


class DeviceCLILineViewSet(NetBoxModelViewSet):
    queryset = DeviceCLILine.objects.prefetch_related("device", "tags")
    serializer_class = DeviceCLILineSerializer
    filterset_class = filtersets.DeviceCLILineFilterSet
