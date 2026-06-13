# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (not the GraphQL-inclusive APIViewTestCase) since the
plugin ships no GraphQL type yet. The per-device singleton configs (OneToOneField to Device)
need a distinct device per created object, so each create_data row targets a fresh device.
"""
from utilities.testing import APIViewTestCases, create_test_device
from netbox_system_services.models import (
    DNSResolverConfig, NTPConfig, NTPServer, SNMPCommunity, SNMPConfig, SNMPTrapTarget,
    SyslogConfig, SyslogServer, SystemConfig,
)


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


class SystemConfigAPITest(_CRUD):
    model = SystemConfig
    brief_fields = ["device", "display", "id", "url"]
    bulk_update_data = {"location": "bulk-room"}

    @classmethod
    def setUpTestData(cls):
        existing = [create_test_device(f"sys-{i}") for i in range(3)]
        SystemConfig.objects.bulk_create([SystemConfig(device=d, location=f"r{i}") for i, d in enumerate(existing)])
        new = [create_test_device(f"sys-new-{i}") for i in range(3)]
        cls.create_data = [
            {"device": new[0].pk, "default_gateway": "192.0.2.1", "location": "A", "contact": "a@x"},
            {"device": new[1].pk, "default_gateway": "192.0.2.2"},
            {"device": new[2].pk, "location": "C"},
        ]


class SNMPConfigAPITest(_CRUD):
    model = SNMPConfig
    brief_fields = ["device", "display", "enabled", "id", "url"]
    bulk_update_data = {"listen_interface": "mgmt"}

    @classmethod
    def setUpTestData(cls):
        existing = [create_test_device(f"snmp-{i}") for i in range(3)]
        SNMPConfig.objects.bulk_create([SNMPConfig(device=d) for d in existing])
        new = [create_test_device(f"snmp-new-{i}") for i in range(3)]
        cls.create_data = [
            {"device": new[0].pk, "enabled": True, "listen_interface": "lan"},
            {"device": new[1].pk, "enabled": False},
            {"device": new[2].pk, "enabled": True, "listen_interface": "wan"},
        ]


class SNMPCommunityAPITest(_CRUD):
    model = SNMPCommunity
    brief_fields = ["access", "display", "id", "name", "url"]
    bulk_update_data = {"restricted": True}

    @classmethod
    def setUpTestData(cls):
        cfg = SNMPConfig.objects.create(device=create_test_device("snmp-com"))
        SNMPCommunity.objects.bulk_create([
            SNMPCommunity(snmp_config=cfg, name="c1", access="ro"),
            SNMPCommunity(snmp_config=cfg, name="c2", access="rw"),
            SNMPCommunity(snmp_config=cfg, name="c3", access="ro", restricted=True),
        ])
        cls.create_data = [
            {"snmp_config": cfg.pk, "name": "k1", "access": "ro"},
            {"snmp_config": cfg.pk, "name": "k2", "access": "rw", "restricted": True},
            {"snmp_config": cfg.pk, "name": "k3", "access": "ro"},
        ]


class SNMPTrapTargetAPITest(_CRUD):
    model = SNMPTrapTarget
    brief_fields = ["display", "id", "port", "target", "url"]
    bulk_update_data = {"version": "v1"}

    @classmethod
    def setUpTestData(cls):
        cfg = SNMPConfig.objects.create(device=create_test_device("snmp-trap"))
        SNMPTrapTarget.objects.bulk_create([
            SNMPTrapTarget(snmp_config=cfg, target="192.0.2.10", community_ref="t1"),
            SNMPTrapTarget(snmp_config=cfg, target="192.0.2.11", port=1162, version="v1"),
            SNMPTrapTarget(snmp_config=cfg, target="192.0.2.12"),
        ])
        cls.create_data = [
            {"snmp_config": cfg.pk, "target": "192.0.2.20", "port": 162, "version": "v2c", "community_ref": "k"},
            {"snmp_config": cfg.pk, "target": "192.0.2.21", "version": "v1"},
            {"snmp_config": cfg.pk, "target": "2001:db8::1", "port": 2162},
        ]


class SyslogConfigAPITest(_CRUD):
    model = SyslogConfig
    brief_fields = ["device", "display", "id", "severity", "url"]
    bulk_update_data = {"retention_days": 30}

    @classmethod
    def setUpTestData(cls):
        existing = [create_test_device(f"slog-{i}") for i in range(3)]
        SyslogConfig.objects.bulk_create([SyslogConfig(device=d) for d in existing])
        new = [create_test_device(f"slog-new-{i}") for i in range(3)]
        cls.create_data = [
            {"device": new[0].pk, "severity": "info", "facility": "local0", "retention_days": 14},
            {"device": new[1].pk, "severity": "error", "facility": "user"},
            {"device": new[2].pk, "severity": "debug", "facility": "local7", "retention_days": 1},
        ]


class SyslogServerAPITest(_CRUD):
    model = SyslogServer
    brief_fields = ["display", "host", "id", "port", "url"]
    bulk_update_data = {"transport": "tcp"}

    @classmethod
    def setUpTestData(cls):
        cfg = SyslogConfig.objects.create(device=create_test_device("slog-srv"))
        SyslogServer.objects.bulk_create([
            SyslogServer(syslog_config=cfg, host="192.0.2.30"),
            SyslogServer(syslog_config=cfg, host="192.0.2.31", port=6514, transport="tls"),
            SyslogServer(syslog_config=cfg, host="2001:db8::2", transport="tcp"),
        ])
        cls.create_data = [
            {"syslog_config": cfg.pk, "host": "192.0.2.40", "port": 514, "transport": "udp"},
            {"syslog_config": cfg.pk, "host": "192.0.2.41", "transport": "tcp"},
            {"syslog_config": cfg.pk, "host": "2001:db8::3", "port": 6514, "transport": "tls"},
        ]


class NTPConfigAPITest(_CRUD):
    model = NTPConfig
    brief_fields = ["device", "display", "enabled", "id", "url"]
    bulk_update_data = {"serve_lan": True}

    @classmethod
    def setUpTestData(cls):
        existing = [create_test_device(f"ntp-{i}") for i in range(3)]
        NTPConfig.objects.bulk_create([NTPConfig(device=d) for d in existing])
        new = [create_test_device(f"ntp-new-{i}") for i in range(3)]
        cls.create_data = [
            {"device": new[0].pk, "enabled": True, "broadcast": False, "serve_lan": True},
            {"device": new[1].pk, "enabled": False},
            {"device": new[2].pk, "enabled": True},
        ]


class NTPServerAPITest(_CRUD):
    model = NTPServer
    brief_fields = ["display", "host", "id", "prefer", "url"]
    bulk_update_data = {"prefer": True}

    @classmethod
    def setUpTestData(cls):
        cfg = NTPConfig.objects.create(device=create_test_device("ntp-srv"), enabled=True)
        NTPServer.objects.bulk_create([
            NTPServer(ntp_config=cfg, host="0.pool.ntp.org"),
            NTPServer(ntp_config=cfg, host="1.pool.ntp.org", prefer=True),
            NTPServer(ntp_config=cfg, host="192.0.2.123"),
        ])
        cls.create_data = [
            {"ntp_config": cfg.pk, "host": "2.pool.ntp.org", "prefer": False},
            {"ntp_config": cfg.pk, "host": "time.example", "prefer": True},
            {"ntp_config": cfg.pk, "host": "192.0.2.124"},
        ]


class DNSResolverConfigAPITest(_CRUD):
    model = DNSResolverConfig
    brief_fields = ["device", "display", "id", "mode", "url"]
    bulk_update_data = {"mode": "dhcp"}

    @classmethod
    def setUpTestData(cls):
        existing = [create_test_device(f"dns-{i}") for i in range(3)]
        DNSResolverConfig.objects.bulk_create([
            DNSResolverConfig(device=d, nameservers=["192.0.2.1"], search_domains=["x.example"])
            for d in existing
        ])
        new = [create_test_device(f"dns-new-{i}") for i in range(3)]
        cls.create_data = [
            {"device": new[0].pk, "mode": "static",
             "nameservers": ["192.0.2.1", "192.0.2.2"], "search_domains": ["corp.example", "lab.example"]},
            {"device": new[1].pk, "mode": "dhcp", "nameservers": [], "search_domains": []},
            {"device": new[2].pk, "mode": "static", "nameservers": ["2001:db8::1"], "search_domains": ["v6.example"]},
        ]
