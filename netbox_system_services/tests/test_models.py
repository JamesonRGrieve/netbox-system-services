# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, constraints, FK/OneToOne behaviour."""
from dcim.models import Interface
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import create_test_device
from netbox_system_services.choices import (
    DNSForwardBackendChoices, DNSResolverModeChoices, SNMPAccessChoices, SNMPVersionChoices,
    SyslogSeverityChoices, SyslogTransportChoices, WakeOnLanModeChoices, ZramAlgorithmChoices,
)
from netbox_system_services.models import (
    DnsForwardZone, DNSResolverConfig, DynamicDNSRecord, HostMemoryConfig, NTPConfig, NTPServer,
    SNMPCommunity, SNMPConfig, SNMPTrapTarget, SyslogConfig, SyslogServer, SystemConfig,
    SystemTunable, WakeOnLanConfig, WakeOnLanTarget,
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

    def test_config_history_count_blank_means_device_default(self):
        self.assertIsNone(SystemConfig.objects.create(device=self.device).config_history_count)

    def test_config_history_count_round_trips(self):
        c = SystemConfig.objects.create(device=self.device, config_history_count=500)
        c.refresh_from_db()
        self.assertEqual(c.config_history_count, 500)
        c.full_clean()

    def test_config_history_count_rejects_zero(self):
        with self.assertRaises(ValidationError):
            SystemConfig(device=self.device, config_history_count=0).full_clean()


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


class DnsForwardZoneModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_defaults_str_color_and_url(self):
        z = DnsForwardZone.objects.create(device=self.device, domain="corp.example", server="192.0.2.53")
        self.assertEqual(z.port, 53)
        self.assertEqual(z.backend, DNSForwardBackendChoices.UNBOUND)
        self.assertFalse(z.tcp_upstream)
        self.assertEqual(z.get_backend_color(), "blue")
        self.assertEqual(str(z), f"{self.device}: corp.example → 192.0.2.53:53")
        self.assertIn("/plugins/system-services/dns-forward-zones/", z.get_absolute_url())

    def test_dnsmasq_backend_color(self):
        z = DnsForwardZone.objects.create(
            device=self.device, domain="lab.example", server="2001:db8::53",
            backend=DNSForwardBackendChoices.DNSMASQ, tcp_upstream=True, port=5353,
        )
        self.assertEqual(z.get_backend_color(), "green")
        self.assertTrue(z.tcp_upstream)

    def test_unique_per_device_domain_server(self):
        DnsForwardZone.objects.create(device=self.device, domain="dup.example", server="192.0.2.53")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DnsForwardZone.objects.create(device=self.device, domain="dup.example", server="192.0.2.53")

    def test_same_domain_different_server_allowed(self):
        DnsForwardZone.objects.create(device=self.device, domain="ha.example", server="192.0.2.1")
        DnsForwardZone.objects.create(device=self.device, domain="ha.example", server="192.0.2.2")
        self.assertEqual(DnsForwardZone.objects.filter(domain="ha.example").count(), 2)


class SystemTunableModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_create_str_and_url(self):
        t = SystemTunable.objects.create(
            device=self.device, name="net.inet.ip.forwarding", value="1", description="route"
        )
        self.assertEqual(str(t), f"{self.device}: net.inet.ip.forwarding=1")
        self.assertIn("/plugins/system-services/system-tunables/", t.get_absolute_url())

    def test_unique_per_device_name(self):
        SystemTunable.objects.create(device=self.device, name="kern.maxfiles", value="1024")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SystemTunable.objects.create(device=self.device, name="kern.maxfiles", value="2048")


class DynamicDNSRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_defaults_str_and_url(self):
        r = DynamicDNSRecord.objects.create(device=self.device, fqdn="home.example")
        self.assertEqual(r.service, "cloudflare")
        self.assertEqual(r.check_ip_method, "web")
        self.assertTrue(r.enabled)
        self.assertEqual(str(r), f"{self.device}: home.example (cloudflare)")
        self.assertIn("/plugins/system-services/dynamic-dns-records/", r.get_absolute_url())

    def test_credential_ref_is_a_key_not_a_secret(self):
        """`credential_ref` is a logical OpenBao key, never the token value."""
        r = DynamicDNSRecord.objects.create(
            device=self.device, fqdn="vpn.example", credential_ref="ddns/cf-token", enabled=False
        )
        self.assertEqual(r.credential_ref, "ddns/cf-token")
        self.assertFalse(r.enabled)

    def test_unique_per_device_fqdn(self):
        DynamicDNSRecord.objects.create(device=self.device, fqdn="dup.example")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DynamicDNSRecord.objects.create(device=self.device, fqdn="dup.example")


class HostMemoryConfigModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")

    def test_create_str_and_url(self):
        c = HostMemoryConfig.objects.create(
            device=self.device, swappiness=10, swap_file_size_mb=2048,
            zram_percent=25, zram_algorithm=ZramAlgorithmChoices.ZSTD, zram_priority=100,
        )
        self.assertEqual(str(c), f"Host Memory: {self.device}")
        self.assertIn("/plugins/system-services/host-memory-config/", c.get_absolute_url())
        self.assertEqual(c.swappiness, 10)
        self.assertEqual(c.zram_algorithm, "zstd")

    def test_defaults_all_unset(self):
        """Every config field is nullable/blank — unset means 'unmanaged'."""
        c = HostMemoryConfig.objects.create(device=self.device)
        self.assertIsNone(c.swappiness)
        self.assertIsNone(c.swap_file_size_mb)
        self.assertIsNone(c.zram_percent)
        self.assertIsNone(c.zram_size_mb)
        self.assertEqual(c.zram_algorithm, "")
        self.assertIsNone(c.zram_priority)

    def test_one_per_device(self):
        HostMemoryConfig.objects.create(device=self.device)
        with self.assertRaises(IntegrityError), transaction.atomic():
            HostMemoryConfig.objects.create(device=self.device)

    def test_zram_percent_and_size_mutually_exclusive(self):
        c = HostMemoryConfig(device=self.device, zram_percent=50, zram_size_mb=1024)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_zram_single_side_is_valid(self):
        HostMemoryConfig(device=self.device, zram_percent=50).clean()
        HostMemoryConfig(device=self.device, zram_size_mb=1024).clean()

    def test_swappiness_upper_bound_enforced(self):
        with self.assertRaises(ValidationError):
            HostMemoryConfig(device=self.device, swappiness=201).full_clean()

    def test_zram_percent_upper_bound_enforced(self):
        with self.assertRaises(ValidationError):
            HostMemoryConfig(device=self.device, zram_percent=101).full_clean()


class WakeOnLanModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("dev1")
        cls.cfg = WakeOnLanConfig.objects.create(device=cls.device, enabled=True, is_waker=True)

    def test_config_defaults_str_and_url(self):
        self.assertEqual(self.cfg.mode, WakeOnLanModeChoices.MAGIC)
        self.assertTrue(self.cfg.enabled)
        self.assertTrue(self.cfg.is_waker)
        self.assertIsNone(self.cfg.interface)
        self.assertEqual(str(self.cfg), f"WoL: {self.device}")
        self.assertIn("/plugins/system-services/wake-on-lan-config/", self.cfg.get_absolute_url())

    def test_be_woken_off_by_default(self):
        c = WakeOnLanConfig.objects.create(device=create_test_device("dev-off"))
        self.assertFalse(c.enabled)
        self.assertFalse(c.is_waker)
        self.assertEqual(c.mode, WakeOnLanModeChoices.MAGIC)

    def test_one_per_device(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            WakeOnLanConfig.objects.create(device=self.device)

    def test_interface_must_belong_to_device(self):
        other = create_test_device("dev-other")
        iface = Interface.objects.create(device=other, name="eth0", type="1000base-t")
        c = WakeOnLanConfig(device=create_test_device("dev-iface"), interface=iface)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_interface_on_same_device_is_valid(self):
        dev = create_test_device("dev-ok")
        iface = Interface.objects.create(device=dev, name="eth0", type="1000base-t")
        WakeOnLanConfig(device=dev, interface=iface, mode=WakeOnLanModeChoices.BROADCAST).clean()

    def test_target_str_url_and_cascade(self):
        target = create_test_device("waketarget")
        t = WakeOnLanTarget.objects.create(config=self.cfg, target_device=target)
        self.assertEqual(str(t), f"{self.device} -> {target}")
        self.assertIn("/plugins/system-services/wake-on-lan-targets/", t.get_absolute_url())
        self.cfg.delete()
        self.assertEqual(WakeOnLanTarget.objects.count(), 0)

    def test_target_unique_per_config(self):
        target = create_test_device("dup-target")
        WakeOnLanTarget.objects.create(config=self.cfg, target_device=target)
        with self.assertRaises(IntegrityError), transaction.atomic():
            WakeOnLanTarget.objects.create(config=self.cfg, target_device=target)
