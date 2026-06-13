# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, constraints, FK/OneToOne behaviour."""
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import create_test_device
from netbox_system_services.choices import (
    DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices, SyslogSeverityChoices,
    SyslogTransportChoices,
)
from netbox_system_services.models import (
    DNSResolverConfig, NTPConfig, NTPServer, SNMPCommunity, SNMPConfig, SNMPTrapTarget,
    SyslogConfig, SyslogServer, SystemConfig,
)


class SystemConfigModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_create_str_and_url(self):
        c = SystemConfig.objects.create(
            device=self.device, default_gateway="192.0.2.1", location="Rack 4", contact="ops@x"
        )
        self.assertEqual(str(c), f"System: {self.device}")
        self.assertIn("/plugins/system-services/system-config/", c.get_absolute_url())
        self.assertEqual(c.default_gateway, "192.0.2.1")

    def test_one_per_device(self):
        SystemConfig.objects.create(device=self.device)
        with self.assertRaises(IntegrityError), transaction.atomic():
            SystemConfig.objects.create(device=self.device)


class SNMPModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")
        cls.snmp = SNMPConfig.objects.create(device=cls.device, listen_interface="lan")

    def test_config_defaults_and_str(self):
        self.assertTrue(self.snmp.enabled)
        self.assertEqual(str(self.snmp), f"SNMP: {self.device}")
        self.assertIn("/plugins/system-services/snmp-config/", self.snmp.get_absolute_url())

    def test_community_secret_name_only(self):
        """`name` is a logical OpenBao key, not the secret string."""
        com = SNMPCommunity.objects.create(snmp_config=self.snmp, name="ro-key", access=SNMPAccessChoices.RO)
        self.assertEqual(str(com), f"{self.device}: ro-key (ro)")
        self.assertEqual(com.get_access_color(), "green")
        self.assertIn("/plugins/system-services/snmp-communities/", com.get_absolute_url())

    def test_community_unique_per_config(self):
        SNMPCommunity.objects.create(snmp_config=self.snmp, name="dup")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SNMPCommunity.objects.create(snmp_config=self.snmp, name="dup")

    def test_trap_target_defaults(self):
        t = SNMPTrapTarget.objects.create(snmp_config=self.snmp, target="192.0.2.50", community_ref="trap-key")
        self.assertEqual(t.port, 162)
        self.assertEqual(t.version, SNMPVersionChoices.V2C)
        self.assertEqual(str(t), f"{self.device}: trap → 192.0.2.50:162")
        self.assertIn("/plugins/system-services/snmp-trap-targets/", t.get_absolute_url())

    def test_communities_cascade_on_config_delete(self):
        SNMPCommunity.objects.create(snmp_config=self.snmp, name="c1")
        SNMPTrapTarget.objects.create(snmp_config=self.snmp, target="192.0.2.9")
        self.snmp.delete()
        self.assertEqual(SNMPCommunity.objects.count(), 0)
        self.assertEqual(SNMPTrapTarget.objects.count(), 0)


class SyslogModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")
        cls.cfg = SyslogConfig.objects.create(device=cls.device, severity=SyslogSeverityChoices.WARNING)

    def test_config_defaults_str_color(self):
        self.assertEqual(self.cfg.retention_days, 7)
        self.assertEqual(self.cfg.facility, "user")
        self.assertEqual(str(self.cfg), f"Syslog: {self.device}")
        self.assertEqual(self.cfg.get_severity_color(), "orange")
        self.assertIn("/plugins/system-services/syslog-config/", self.cfg.get_absolute_url())

    def test_server_defaults_and_str(self):
        s = SyslogServer.objects.create(syslog_config=self.cfg, host="192.0.2.20", transport=SyslogTransportChoices.TLS)
        self.assertEqual(s.port, 514)
        self.assertEqual(str(s), f"{self.device}: 192.0.2.20:514/tls")
        self.assertIn("/plugins/system-services/syslog-servers/", s.get_absolute_url())


class NTPModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")
        cls.cfg = NTPConfig.objects.create(device=cls.device, enabled=True)

    def test_config_defaults_str(self):
        self.assertTrue(self.cfg.broadcast)
        self.assertFalse(self.cfg.serve_lan)
        self.assertEqual(str(self.cfg), f"NTP: {self.device}")
        self.assertIn("/plugins/system-services/ntp-config/", self.cfg.get_absolute_url())

    def test_server_str_and_prefer(self):
        s = NTPServer.objects.create(ntp_config=self.cfg, host="0.pool.ntp.org", prefer=True)
        self.assertTrue(s.prefer)
        self.assertEqual(str(s), f"{self.device}: 0.pool.ntp.org")
        self.assertIn("/plugins/system-services/ntp-servers/", s.get_absolute_url())


class DNSResolverConfigModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_create_arrays_ordered_and_str(self):
        c = DNSResolverConfig.objects.create(
            device=self.device,
            mode=DNSResolverModeChoices.STATIC,
            nameservers=["192.0.2.1", "192.0.2.2", "2001:db8::1"],
            search_domains=["corp.example", "lab.example"],
        )
        c.refresh_from_db()
        # Array order is significant (resolver query order) and must survive a round-trip.
        self.assertEqual(c.nameservers, ["192.0.2.1", "192.0.2.2", "2001:db8::1"])
        self.assertEqual(c.search_domains, ["corp.example", "lab.example"])
        self.assertEqual(c.get_mode_color(), "blue")
        self.assertEqual(str(c), f"DNS resolver: {self.device}")
        self.assertIn("/plugins/system-services/dns-resolver-config/", c.get_absolute_url())

    def test_defaults_empty_arrays(self):
        c = DNSResolverConfig.objects.create(device=self.device, mode=DNSResolverModeChoices.DHCP)
        self.assertEqual(c.nameservers, [])
        self.assertEqual(c.search_domains, [])
        self.assertEqual(c.get_mode_color(), "green")
