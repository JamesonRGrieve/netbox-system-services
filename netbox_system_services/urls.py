# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views


def _routes(slug, name, model, list_view, edit_view, detail_view, delete_view, bulk_delete_view):
    return [
        path(f"{slug}/", list_view.as_view(), name=f"{name}_list"),
        path(f"{slug}/add/", edit_view.as_view(), name=f"{name}_add"),
        path(f"{slug}/delete/", bulk_delete_view.as_view(), name=f"{name}_bulk_delete"),
        path(f"{slug}/<int:pk>/", detail_view.as_view(), name=name),
        path(f"{slug}/<int:pk>/edit/", edit_view.as_view(), name=f"{name}_edit"),
        path(f"{slug}/<int:pk>/delete/", delete_view.as_view(), name=f"{name}_delete"),
        path(f"{slug}/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name=f"{name}_changelog", kwargs={"model": model}),
        path(f"{slug}/<int:pk>/journal/", ObjectJournalView.as_view(), name=f"{name}_journal", kwargs={"model": model}),
    ]


urlpatterns = [
    *_routes("system-config", "systemconfig", models.SystemConfig,
             views.SystemConfigListView, views.SystemConfigEditView, views.SystemConfigView,
             views.SystemConfigDeleteView, views.SystemConfigBulkDeleteView),
    *_routes("snmp-config", "snmpconfig", models.SNMPConfig,
             views.SNMPConfigListView, views.SNMPConfigEditView, views.SNMPConfigView,
             views.SNMPConfigDeleteView, views.SNMPConfigBulkDeleteView),
    *_routes("snmp-communities", "snmpcommunity", models.SNMPCommunity,
             views.SNMPCommunityListView, views.SNMPCommunityEditView, views.SNMPCommunityView,
             views.SNMPCommunityDeleteView, views.SNMPCommunityBulkDeleteView),
    *_routes("snmp-trap-targets", "snmptraptarget", models.SNMPTrapTarget,
             views.SNMPTrapTargetListView, views.SNMPTrapTargetEditView, views.SNMPTrapTargetView,
             views.SNMPTrapTargetDeleteView, views.SNMPTrapTargetBulkDeleteView),
    *_routes("syslog-config", "syslogconfig", models.SyslogConfig,
             views.SyslogConfigListView, views.SyslogConfigEditView, views.SyslogConfigView,
             views.SyslogConfigDeleteView, views.SyslogConfigBulkDeleteView),
    *_routes("syslog-servers", "syslogserver", models.SyslogServer,
             views.SyslogServerListView, views.SyslogServerEditView, views.SyslogServerView,
             views.SyslogServerDeleteView, views.SyslogServerBulkDeleteView),
    *_routes("ntp-config", "ntpconfig", models.NTPConfig,
             views.NTPConfigListView, views.NTPConfigEditView, views.NTPConfigView,
             views.NTPConfigDeleteView, views.NTPConfigBulkDeleteView),
    *_routes("ntp-servers", "ntpserver", models.NTPServer,
             views.NTPServerListView, views.NTPServerEditView, views.NTPServerView,
             views.NTPServerDeleteView, views.NTPServerBulkDeleteView),
    *_routes("dns-resolver-config", "dnsresolverconfig", models.DNSResolverConfig,
             views.DNSResolverConfigListView, views.DNSResolverConfigEditView, views.DNSResolverConfigView,
             views.DNSResolverConfigDeleteView, views.DNSResolverConfigBulkDeleteView),
]
