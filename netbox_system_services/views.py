# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class SystemConfigView(generic.ObjectView):
    queryset = models.SystemConfig.objects.all()


class SystemConfigListView(generic.ObjectListView):
    queryset = models.SystemConfig.objects.all()
    table = tables.SystemConfigTable
    filterset = filtersets.SystemConfigFilterSet
    filterset_form = forms.SystemConfigFilterForm


class SystemConfigEditView(generic.ObjectEditView):
    queryset = models.SystemConfig.objects.all()
    form = forms.SystemConfigForm


class SystemConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.SystemConfig.objects.all()


class SystemConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SystemConfig.objects.all()
    table = tables.SystemConfigTable


class SNMPConfigView(generic.ObjectView):
    queryset = models.SNMPConfig.objects.all()


class SNMPConfigListView(generic.ObjectListView):
    queryset = models.SNMPConfig.objects.all()
    table = tables.SNMPConfigTable
    filterset = filtersets.SNMPConfigFilterSet
    filterset_form = forms.SNMPConfigFilterForm


class SNMPConfigEditView(generic.ObjectEditView):
    queryset = models.SNMPConfig.objects.all()
    form = forms.SNMPConfigForm


class SNMPConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.SNMPConfig.objects.all()


class SNMPConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SNMPConfig.objects.all()
    table = tables.SNMPConfigTable


class SNMPCommunityView(generic.ObjectView):
    queryset = models.SNMPCommunity.objects.all()


class SNMPCommunityListView(generic.ObjectListView):
    queryset = models.SNMPCommunity.objects.all()
    table = tables.SNMPCommunityTable
    filterset = filtersets.SNMPCommunityFilterSet
    filterset_form = forms.SNMPCommunityFilterForm


class SNMPCommunityEditView(generic.ObjectEditView):
    queryset = models.SNMPCommunity.objects.all()
    form = forms.SNMPCommunityForm


class SNMPCommunityDeleteView(generic.ObjectDeleteView):
    queryset = models.SNMPCommunity.objects.all()


class SNMPCommunityBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SNMPCommunity.objects.all()
    table = tables.SNMPCommunityTable


class SNMPTrapTargetView(generic.ObjectView):
    queryset = models.SNMPTrapTarget.objects.all()


class SNMPTrapTargetListView(generic.ObjectListView):
    queryset = models.SNMPTrapTarget.objects.all()
    table = tables.SNMPTrapTargetTable
    filterset = filtersets.SNMPTrapTargetFilterSet
    filterset_form = forms.SNMPTrapTargetFilterForm


class SNMPTrapTargetEditView(generic.ObjectEditView):
    queryset = models.SNMPTrapTarget.objects.all()
    form = forms.SNMPTrapTargetForm


class SNMPTrapTargetDeleteView(generic.ObjectDeleteView):
    queryset = models.SNMPTrapTarget.objects.all()


class SNMPTrapTargetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SNMPTrapTarget.objects.all()
    table = tables.SNMPTrapTargetTable


class SyslogConfigView(generic.ObjectView):
    queryset = models.SyslogConfig.objects.all()


class SyslogConfigListView(generic.ObjectListView):
    queryset = models.SyslogConfig.objects.all()
    table = tables.SyslogConfigTable
    filterset = filtersets.SyslogConfigFilterSet
    filterset_form = forms.SyslogConfigFilterForm


class SyslogConfigEditView(generic.ObjectEditView):
    queryset = models.SyslogConfig.objects.all()
    form = forms.SyslogConfigForm


class SyslogConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.SyslogConfig.objects.all()


class SyslogConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SyslogConfig.objects.all()
    table = tables.SyslogConfigTable


class SyslogServerView(generic.ObjectView):
    queryset = models.SyslogServer.objects.all()


class SyslogServerListView(generic.ObjectListView):
    queryset = models.SyslogServer.objects.all()
    table = tables.SyslogServerTable
    filterset = filtersets.SyslogServerFilterSet
    filterset_form = forms.SyslogServerFilterForm


class SyslogServerEditView(generic.ObjectEditView):
    queryset = models.SyslogServer.objects.all()
    form = forms.SyslogServerForm


class SyslogServerDeleteView(generic.ObjectDeleteView):
    queryset = models.SyslogServer.objects.all()


class SyslogServerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SyslogServer.objects.all()
    table = tables.SyslogServerTable


class NTPConfigView(generic.ObjectView):
    queryset = models.NTPConfig.objects.all()


class NTPConfigListView(generic.ObjectListView):
    queryset = models.NTPConfig.objects.all()
    table = tables.NTPConfigTable
    filterset = filtersets.NTPConfigFilterSet
    filterset_form = forms.NTPConfigFilterForm


class NTPConfigEditView(generic.ObjectEditView):
    queryset = models.NTPConfig.objects.all()
    form = forms.NTPConfigForm


class NTPConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.NTPConfig.objects.all()


class NTPConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NTPConfig.objects.all()
    table = tables.NTPConfigTable


class NTPServerView(generic.ObjectView):
    queryset = models.NTPServer.objects.all()


class NTPServerListView(generic.ObjectListView):
    queryset = models.NTPServer.objects.all()
    table = tables.NTPServerTable
    filterset = filtersets.NTPServerFilterSet
    filterset_form = forms.NTPServerFilterForm


class NTPServerEditView(generic.ObjectEditView):
    queryset = models.NTPServer.objects.all()
    form = forms.NTPServerForm


class NTPServerDeleteView(generic.ObjectDeleteView):
    queryset = models.NTPServer.objects.all()


class NTPServerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NTPServer.objects.all()
    table = tables.NTPServerTable


class DNSResolverConfigView(generic.ObjectView):
    queryset = models.DNSResolverConfig.objects.all()


class DNSResolverConfigListView(generic.ObjectListView):
    queryset = models.DNSResolverConfig.objects.all()
    table = tables.DNSResolverConfigTable
    filterset = filtersets.DNSResolverConfigFilterSet
    filterset_form = forms.DNSResolverConfigFilterForm


class DNSResolverConfigEditView(generic.ObjectEditView):
    queryset = models.DNSResolverConfig.objects.all()
    form = forms.DNSResolverConfigForm


class DNSResolverConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.DNSResolverConfig.objects.all()


class DNSResolverConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DNSResolverConfig.objects.all()
    table = tables.DNSResolverConfigTable


class DnsForwardZoneView(generic.ObjectView):
    queryset = models.DnsForwardZone.objects.all()


class DnsForwardZoneListView(generic.ObjectListView):
    queryset = models.DnsForwardZone.objects.all()
    table = tables.DnsForwardZoneTable
    filterset = filtersets.DnsForwardZoneFilterSet
    filterset_form = forms.DnsForwardZoneFilterForm


class DnsForwardZoneEditView(generic.ObjectEditView):
    queryset = models.DnsForwardZone.objects.all()
    form = forms.DnsForwardZoneForm


class DnsForwardZoneDeleteView(generic.ObjectDeleteView):
    queryset = models.DnsForwardZone.objects.all()


class DnsForwardZoneBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DnsForwardZone.objects.all()
    table = tables.DnsForwardZoneTable


class SystemTunableView(generic.ObjectView):
    queryset = models.SystemTunable.objects.all()


class SystemTunableListView(generic.ObjectListView):
    queryset = models.SystemTunable.objects.all()
    table = tables.SystemTunableTable
    filterset = filtersets.SystemTunableFilterSet
    filterset_form = forms.SystemTunableFilterForm


class SystemTunableEditView(generic.ObjectEditView):
    queryset = models.SystemTunable.objects.all()
    form = forms.SystemTunableForm


class SystemTunableDeleteView(generic.ObjectDeleteView):
    queryset = models.SystemTunable.objects.all()


class SystemTunableBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SystemTunable.objects.all()
    table = tables.SystemTunableTable


class DynamicDNSRecordView(generic.ObjectView):
    queryset = models.DynamicDNSRecord.objects.all()


class DynamicDNSRecordListView(generic.ObjectListView):
    queryset = models.DynamicDNSRecord.objects.all()
    table = tables.DynamicDNSRecordTable
    filterset = filtersets.DynamicDNSRecordFilterSet
    filterset_form = forms.DynamicDNSRecordFilterForm


class DynamicDNSRecordEditView(generic.ObjectEditView):
    queryset = models.DynamicDNSRecord.objects.all()
    form = forms.DynamicDNSRecordForm


class DynamicDNSRecordDeleteView(generic.ObjectDeleteView):
    queryset = models.DynamicDNSRecord.objects.all()


class DynamicDNSRecordBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DynamicDNSRecord.objects.all()
    table = tables.DynamicDNSRecordTable


class HostMemoryConfigView(generic.ObjectView):
    queryset = models.HostMemoryConfig.objects.all()


class HostMemoryConfigListView(generic.ObjectListView):
    queryset = models.HostMemoryConfig.objects.all()
    table = tables.HostMemoryConfigTable
    filterset = filtersets.HostMemoryConfigFilterSet
    filterset_form = forms.HostMemoryConfigFilterForm


class HostMemoryConfigEditView(generic.ObjectEditView):
    queryset = models.HostMemoryConfig.objects.all()
    form = forms.HostMemoryConfigForm


class HostMemoryConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.HostMemoryConfig.objects.all()


class HostMemoryConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.HostMemoryConfig.objects.all()
    table = tables.HostMemoryConfigTable


class WakeOnLanConfigView(generic.ObjectView):
    queryset = models.WakeOnLanConfig.objects.all()


class WakeOnLanConfigListView(generic.ObjectListView):
    queryset = models.WakeOnLanConfig.objects.all()
    table = tables.WakeOnLanConfigTable
    filterset = filtersets.WakeOnLanConfigFilterSet
    filterset_form = forms.WakeOnLanConfigFilterForm


class WakeOnLanConfigEditView(generic.ObjectEditView):
    queryset = models.WakeOnLanConfig.objects.all()
    form = forms.WakeOnLanConfigForm


class WakeOnLanConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.WakeOnLanConfig.objects.all()


class WakeOnLanConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.WakeOnLanConfig.objects.all()
    table = tables.WakeOnLanConfigTable


class WakeOnLanTargetView(generic.ObjectView):
    queryset = models.WakeOnLanTarget.objects.all()


class WakeOnLanTargetListView(generic.ObjectListView):
    queryset = models.WakeOnLanTarget.objects.all()
    table = tables.WakeOnLanTargetTable
    filterset = filtersets.WakeOnLanTargetFilterSet
    filterset_form = forms.WakeOnLanTargetFilterForm


class WakeOnLanTargetEditView(generic.ObjectEditView):
    queryset = models.WakeOnLanTarget.objects.all()
    form = forms.WakeOnLanTargetForm


class WakeOnLanTargetDeleteView(generic.ObjectDeleteView):
    queryset = models.WakeOnLanTarget.objects.all()


class WakeOnLanTargetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.WakeOnLanTarget.objects.all()
    table = tables.WakeOnLanTargetTable
