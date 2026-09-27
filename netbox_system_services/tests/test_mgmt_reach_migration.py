# SPDX-License-Identifier: AGPL-3.0-or-later
"""The 0010 data migration, exercised against a real DB (no mocks).

Its forward/backward functions take Django's ``apps`` registry, so they are invoked here with the
live registry — the same code path the migration runs. The module name starts with a digit, so it
is loaded via :mod:`importlib`.

The behaviour that makes it safe on prod: values carried across, a SystemConfig row created for a
device that has values but no row yet, an existing non-default value never overwritten on re-run,
a literal ``False`` treated as a value rather than as absent, and a faithful round trip back into
``custom_field_data``.
"""
from importlib import import_module

from django.apps import apps as global_apps
from django.test import TestCase
from utilities.testing import create_test_device
from netbox_system_services.models import SystemConfig

_mig = import_module("netbox_system_services.migrations.0010_device_custom_fields_to_systemconfig")
forward = _mig.forward
backward = _mig.backward


class MgmtReachMigrationTest(TestCase):
    def _run(self):
        forward(global_apps, None)

    def test_creates_the_row_for_a_device_that_has_none(self):
        dev = create_test_device("edge-1")
        dev.custom_field_data = {"ssh_host": "192.0.2.10", "ssh_user": "root"}
        dev.save()
        self.assertFalse(SystemConfig.objects.filter(device=dev).exists())
        self._run()
        cfg = SystemConfig.objects.get(device=dev)
        self.assertEqual(cfg.ssh_host, "192.0.2.10")
        self.assertEqual(cfg.ssh_user, "root")

    def test_fills_an_existing_row(self):
        dev = create_test_device("edge-2")
        SystemConfig.objects.create(device=dev, fqdn="edge-2.example.com")
        dev.custom_field_data = {"ssh_host": "192.0.2.11", "vlan_trunk": "re0"}
        dev.save()
        self._run()
        cfg = SystemConfig.objects.get(device=dev)
        self.assertEqual(cfg.ssh_host, "192.0.2.11")
        self.assertEqual(cfg.vlan_trunk, "re0")
        self.assertEqual(cfg.fqdn, "edge-2.example.com", "must not disturb existing fields")

    def test_false_is_a_value_not_an_absence(self):
        dev = create_test_device("edge-3")
        dev.custom_field_data = {"openwrt_network_reload": False, "manage_lan": False}
        dev.save()
        self._run()
        cfg = SystemConfig.objects.get(device=dev)
        self.assertFalse(cfg.openwrt_network_reload, "a reload-unsafe box must stay opted OUT")
        self.assertFalse(cfg.manage_lan)

    def test_true_on_a_default_false_toggle_is_carried(self):
        dev = create_test_device("edge-4")
        dev.custom_field_data = {"manage_base_lan": True, "openwrt_native_dsa": True}
        dev.save()
        self._run()
        cfg = SystemConfig.objects.get(device=dev)
        self.assertTrue(cfg.manage_base_lan)
        self.assertTrue(cfg.openwrt_native_dsa)

    def test_device_with_nothing_recorded_gets_no_row(self):
        create_test_device("edge-5")
        self._run()
        self.assertFalse(SystemConfig.objects.filter(device__name="edge-5").exists())

    def test_empty_string_counts_as_absent(self):
        dev = create_test_device("edge-6")
        dev.custom_field_data = {"ssh_host": "", "ssh_user": ""}
        dev.save()
        self._run()
        self.assertFalse(SystemConfig.objects.filter(device=dev).exists())

    def test_rerun_does_not_clobber_an_edit(self):
        dev = create_test_device("edge-7")
        dev.custom_field_data = {"ssh_host": "192.0.2.20"}
        dev.save()
        self._run()
        cfg = SystemConfig.objects.get(device=dev)
        cfg.ssh_host = "192.0.2.99"
        cfg.save()
        self._run()
        cfg.refresh_from_db()
        self.assertEqual(cfg.ssh_host, "192.0.2.99")
        self.assertEqual(SystemConfig.objects.filter(device=dev).count(), 1)

    def test_backward_restores_custom_field_data(self):
        dev = create_test_device("edge-8")
        original = {"ssh_host": "192.0.2.30", "ssh_user": "root", "vlan_trunk": "re0",
                    "manage_reconcile": False}
        dev.custom_field_data = dict(original)
        dev.save()
        self._run()
        dev.custom_field_data = {}
        dev.save()

        backward(global_apps, None)

        dev.refresh_from_db()
        for key, value in original.items():
            self.assertEqual(dev.custom_field_data.get(key), value, msg=key)

    def test_backward_omits_fields_left_at_their_default(self):
        dev = create_test_device("edge-9")
        dev.custom_field_data = {"ssh_host": "192.0.2.40"}
        dev.save()
        self._run()
        dev.custom_field_data = {}
        dev.save()

        backward(global_apps, None)

        dev.refresh_from_db()
        self.assertEqual(dev.custom_field_data.get("ssh_host"), "192.0.2.40")
        self.assertNotIn("manage_lan", dev.custom_field_data,
                         "a field still at its default is not an override and must not be written")
