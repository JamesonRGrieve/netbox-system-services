# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_system_services"

router = NetBoxRouter()
router.register("system-config", views.SystemConfigViewSet)
router.register("snmp-config", views.SNMPConfigViewSet)
router.register("snmp-communities", views.SNMPCommunityViewSet)
router.register("snmp-trap-targets", views.SNMPTrapTargetViewSet)
router.register("syslog-config", views.SyslogConfigViewSet)
router.register("syslog-servers", views.SyslogServerViewSet)
router.register("ntp-config", views.NTPConfigViewSet)
router.register("ntp-servers", views.NTPServerViewSet)
router.register("dns-resolver-config", views.DNSResolverConfigViewSet)

urlpatterns = router.urls
