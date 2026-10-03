# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks)."""
from django.test import TestCase
from utilities.testing import create_test_device
from netbox_system_services.choices import (
    DNSForwardBackendChoices, DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices,
    SyslogSeverityChoices, SyslogTransportChoices, WakeOnLanModeChoices, ZramAlgorithmChoices,
)
from netbox_system_services.filtersets import (
    DnsForwardZoneFilterSet, DNSResolverConfigFilterSet, DynamicDNSRecordFilterSet,
    HostMemoryConfigFilterSet, NTPConfigFilterSet, NTPServerFilterSet, SNMPCommunityFilterSet,
    SNMPConfigFilterSet, SNMPTrapTargetFilterSet, SyslogConfigFilterSet, SyslogServerFilterSet,
    SystemConfigFilterSet, SystemTunableFilterSet, WakeOnLanConfigFilterSet, WakeOnLanTargetFilterSet,
)
from netbox_system_services.models import (
    DnsForwardZone, DNSResolverConfig, DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
)


class SystemConfigFilterSetTest(TestCase):
    queryset = SystemConfig.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        SystemConfig.objects.create(device=cls.d1, location="DC-A", contact="a@x", config_history_count=500)
        SystemConfig.objects.create(device=cls.d2, location="DC-B", contact="b@x")

    def test_device_id_scopes(self):
        self.assertEqual(SystemConfigFilterSet({"device_id": [self.d1.pk]}, self.queryset).qs.count(), 1)

    def test_device_name(self):
        self.assertEqual(SystemConfigFilterSet({"device": [self.d2.name]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(SystemConfigFilterSet({"q": "DC-A"}, self.queryset).qs.count(), 1)

    def test_config_history_count(self):
        qs = SystemConfigFilterSet({"config_history_count": [500]}, self.queryset).qs
        self.assertEqual(list(qs.values_list("device", flat=True)), [self.d1.pk])


class SNMPFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        cls.c1 = SNMPConfig.objects.create(device=cls.d1, listen_interface="lan")
        cls.c2 = SNMPConfig.objects.create(device=cls.d2, enabled=False)
        SNMPCommunity.objects.bulk_create([
            SNMPCommunity(snmp_config=cls.c1, name="ro1", access=SNMPAccessChoices.RO),
            SNMPCommunity(snmp_config=cls.c1, name="rw1", access=SNMPAccessChoices.RW),
            SNMPCommunity(snmp_config=cls.c2, name="ro2", access=SNMPAccessChoices.RO),
        ])
        SNMPTrapTarget.objects.bulk_create([
            SNMPTrapTarget(snmp_config=cls.c1, target="192.0.2.10", version=SNMPVersionChoices.V2C),
            SNMPTrapTarget(snmp_config=cls.c1, target="192.0.2.11", version=SNMPVersionChoices.V1),
        ])

    def test_config_enabled(self):
        self.assertEqual(SNMPConfigFilterSet({"enabled": True}, SNMPConfig.objects.all()).qs.count(), 1)

    def test_config_device_id(self):
        self.assertEqual(SNMPConfigFilterSet({"device_id": [self.d1.pk]}, SNMPConfig.objects.all()).qs.count(), 1)

    def test_community_config_scope_and_access(self):
        qs = SNMPCommunity.objects.all()
        self.assertEqual(SNMPCommunityFilterSet({"snmp_config_id": [self.c1.pk]}, qs).qs.count(), 2)
        self.assertEqual(SNMPCommunityFilterSet({"access": [SNMPAccessChoices.RO]}, qs).qs.count(), 2)

    def test_community_search(self):
        self.assertEqual(SNMPCommunityFilterSet({"q": "rw1"}, SNMPCommunity.objects.all()).qs.count(), 1)

    def test_trap_version(self):
        qs = SNMPTrapTarget.objects.all()
        self.assertEqual(SNMPTrapTargetFilterSet({"version": [SNMPVersionChoices.V1]}, qs).qs.count(), 1)
        self.assertEqual(SNMPTrapTargetFilterSet({"snmp_config_id": [self.c1.pk]}, qs).qs.count(), 2)


class SyslogFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        cls.c1 = SyslogConfig.objects.create(device=cls.d1, severity=SyslogSeverityChoices.WARNING)
        cls.c2 = SyslogConfig.objects.create(device=cls.d2, severity=SyslogSeverityChoices.ERROR)
        SyslogServer.objects.bulk_create([
            SyslogServer(syslog_config=cls.c1, host="192.0.2.30", transport=SyslogTransportChoices.UDP),
            SyslogServer(syslog_config=cls.c1, host="192.0.2.31", transport=SyslogTransportChoices.TLS),
            SyslogServer(syslog_config=cls.c2, host="192.0.2.32", transport=SyslogTransportChoices.TCP),
        ])

    def test_config_severity(self):
        self.assertEqual(
            SyslogConfigFilterSet({"severity": [SyslogSeverityChoices.WARNING]}, SyslogConfig.objects.all()).qs.count(), 1
        )

    def test_server_config_scope_and_transport(self):
        qs = SyslogServer.objects.all()
        self.assertEqual(SyslogServerFilterSet({"syslog_config_id": [self.c1.pk]}, qs).qs.count(), 2)
        self.assertEqual(SyslogServerFilterSet({"transport": [SyslogTransportChoices.TLS]}, qs).qs.count(), 1)

    def test_server_search(self):
        self.assertEqual(SyslogServerFilterSet({"q": "192.0.2.32"}, SyslogServer.objects.all()).qs.count(), 1)


class NTPFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        cls.c1 = NTPConfig.objects.create(device=cls.d1, enabled=True, serve_lan=True)
        cls.c2 = NTPConfig.objects.create(device=cls.d2, enabled=False)
        NTPServer.objects.bulk_create([
            NTPServer(ntp_config=cls.c1, host="0.pool.ntp.org", prefer=True),
            NTPServer(ntp_config=cls.c1, host="1.pool.ntp.org"),
            NTPServer(ntp_config=cls.c2, host="time.example"),
        ])

    def test_config_serve_lan(self):
        self.assertEqual(NTPConfigFilterSet({"serve_lan": True}, NTPConfig.objects.all()).qs.count(), 1)

    def test_server_config_scope_and_prefer(self):
        qs = NTPServer.objects.all()
        self.assertEqual(NTPServerFilterSet({"ntp_config_id": [self.c1.pk]}, qs).qs.count(), 2)
        self.assertEqual(NTPServerFilterSet({"prefer": True}, qs).qs.count(), 1)

    def test_server_search(self):
        self.assertEqual(NTPServerFilterSet({"q": "time.example"}, NTPServer.objects.all()).qs.count(), 1)


class DNSResolverConfigFilterSetTest(TestCase):
    queryset = DNSResolverConfig.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        DNSResolverConfig.objects.create(device=cls.d1, mode=DNSResolverModeChoices.STATIC, nameservers=["192.0.2.1"])
        DNSResolverConfig.objects.create(device=cls.d2, mode=DNSResolverModeChoices.DHCP)

    def test_mode(self):
        self.assertEqual(DNSResolverConfigFilterSet({"mode": [DNSResolverModeChoices.STATIC]}, self.queryset).qs.count(), 1)

    def test_device_id(self):
        self.assertEqual(DNSResolverConfigFilterSet({"device_id": [self.d2.pk]}, self.queryset).qs.count(), 1)


class DnsForwardZoneFilterSetTest(TestCase):
    queryset = DnsForwardZone.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        DnsForwardZone.objects.bulk_create([
            DnsForwardZone(device=cls.d1, domain="corp.example", server="192.0.2.53", backend=DNSForwardBackendChoices.UNBOUND),
            DnsForwardZone(device=cls.d1, domain="lab.example", server="192.0.2.54", backend=DNSForwardBackendChoices.DNSMASQ),
            DnsForwardZone(device=cls.d2, domain="dmz.example", server="192.0.2.55", backend=DNSForwardBackendChoices.UNBOUND),
        ])

    def test_device_id_scopes(self):
        self.assertEqual(DnsForwardZoneFilterSet({"device_id": [self.d1.pk]}, self.queryset).qs.count(), 2)

    def test_backend(self):
        self.assertEqual(
            DnsForwardZoneFilterSet({"backend": [DNSForwardBackendChoices.DNSMASQ]}, self.queryset).qs.count(), 1
        )

    def test_search(self):
        self.assertEqual(DnsForwardZoneFilterSet({"q": "corp.example"}, self.queryset).qs.count(), 1)


class SystemTunableFilterSetTest(TestCase):
    queryset = SystemTunable.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        SystemTunable.objects.bulk_create([
            SystemTunable(device=cls.d1, name="net.inet.ip.forwarding", value="1"),
            SystemTunable(device=cls.d1, name="kern.maxfiles", value="65536"),
            SystemTunable(device=cls.d2, name="net.inet6.ip6.forwarding", value="1"),
        ])

    def test_device_id_scopes(self):
        self.assertEqual(SystemTunableFilterSet({"device_id": [self.d1.pk]}, self.queryset).qs.count(), 2)

    def test_search(self):
        self.assertEqual(SystemTunableFilterSet({"q": "kern.maxfiles"}, self.queryset).qs.count(), 1)


class DynamicDNSRecordFilterSetTest(TestCase):
    queryset = DynamicDNSRecord.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        DynamicDNSRecord.objects.bulk_create([
            DynamicDNSRecord(device=cls.d1, fqdn="home.example", service="cloudflare", enabled=True),
            DynamicDNSRecord(device=cls.d1, fqdn="vpn.example", service="route53", enabled=False),
            DynamicDNSRecord(device=cls.d2, fqdn="dmz.example", service="cloudflare", enabled=True),
        ])

    def test_device_id_scopes(self):
        self.assertEqual(DynamicDNSRecordFilterSet({"device_id": [self.d1.pk]}, self.queryset).qs.count(), 2)

    def test_enabled(self):
        self.assertEqual(DynamicDNSRecordFilterSet({"enabled": True}, self.queryset).qs.count(), 2)

    def test_search(self):
        self.assertEqual(DynamicDNSRecordFilterSet({"q": "vpn.example"}, self.queryset).qs.count(), 1)


class HostMemoryConfigFilterSetTest(TestCase):
    queryset = HostMemoryConfig.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        HostMemoryConfig.objects.create(device=cls.d1, swappiness=10, zram_algorithm=ZramAlgorithmChoices.ZSTD)
        HostMemoryConfig.objects.create(device=cls.d2, swappiness=60, zram_algorithm=ZramAlgorithmChoices.LZ4)

    def test_device_id_scopes(self):
        self.assertEqual(HostMemoryConfigFilterSet({"device_id": [self.d1.pk]}, self.queryset).qs.count(), 1)

    def test_zram_algorithm(self):
        self.assertEqual(
            HostMemoryConfigFilterSet({"zram_algorithm": [ZramAlgorithmChoices.ZSTD]}, self.queryset).qs.count(), 1
        )

    def test_swappiness_exact(self):
        self.assertEqual(HostMemoryConfigFilterSet({"swappiness": [10]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(HostMemoryConfigFilterSet({"q": self.d1.name}, self.queryset).qs.count(), 1)


class WakeOnLanFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = create_test_device("dev1")
        cls.d2 = create_test_device("dev2")
        cls.c1 = WakeOnLanConfig.objects.create(
            device=cls.d1, enabled=True, is_waker=True, mode=WakeOnLanModeChoices.MAGIC
        )
        cls.c2 = WakeOnLanConfig.objects.create(
            device=cls.d2, enabled=False, mode=WakeOnLanModeChoices.BROADCAST
        )
        cls.t1 = create_test_device("target1")
        cls.t2 = create_test_device("target2")
        WakeOnLanTarget.objects.bulk_create([
            WakeOnLanTarget(config=cls.c1, target_device=cls.t1),
            WakeOnLanTarget(config=cls.c1, target_device=cls.t2),
            WakeOnLanTarget(config=cls.c2, target_device=cls.t1),
        ])

    def test_config_device_id(self):
        self.assertEqual(
            WakeOnLanConfigFilterSet({"device_id": [self.d1.pk]}, WakeOnLanConfig.objects.all()).qs.count(), 1
        )

    def test_config_is_waker_and_mode(self):
        qs = WakeOnLanConfig.objects.all()
        self.assertEqual(WakeOnLanConfigFilterSet({"is_waker": True}, qs).qs.count(), 1)
        self.assertEqual(WakeOnLanConfigFilterSet({"mode": [WakeOnLanModeChoices.BROADCAST]}, qs).qs.count(), 1)

    def test_config_search(self):
        self.assertEqual(
            WakeOnLanConfigFilterSet({"q": self.d1.name}, WakeOnLanConfig.objects.all()).qs.count(), 1
        )

    def test_target_config_scope(self):
        self.assertEqual(
            WakeOnLanTargetFilterSet({"config_id": [self.c1.pk]}, WakeOnLanTarget.objects.all()).qs.count(), 2
        )

    def test_target_device_scope(self):
        self.assertEqual(
            WakeOnLanTargetFilterSet({"target_device_id": [self.t1.pk]}, WakeOnLanTarget.objects.all()).qs.count(), 2
        )

    def test_target_search(self):
        self.assertEqual(
            WakeOnLanTargetFilterSet({"q": self.t2.name}, WakeOnLanTarget.objects.all()).qs.count(), 1
        )
