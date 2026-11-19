# SPDX-License-Identifier: AGPL-3.0-or-later
"""Device access groups and local accounts, against a real DB (no mocks): constraints, the
group-on-the-same-device rule, and the secret_ref rules (a path to a tier leaf, never a key)."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.deletion import RestrictedError
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import APIViewTestCases, create_test_device
from netbox_system_services.models import DeviceAccessGroup, DeviceLocalAccount

REF = "prod/boden/infra/hq/hq-opnsense/readonly"


class DeviceAccessGroupModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("fw1")

    def test_create_str_url_and_privileges(self):
        g = DeviceAccessGroup.objects.create(
            device=self.device, name="readonly", privileges=["page-all", "user-config-readonly"]
        )
        g.full_clean()
        g.refresh_from_db()
        self.assertEqual(str(g), f"{self.device}: readonly")
        self.assertIn("/plugins/system-services/device-access-groups/", g.get_absolute_url())
        self.assertEqual(g.privileges, ["page-all", "user-config-readonly"])

    def test_privileges_default_empty(self):
        self.assertEqual(DeviceAccessGroup.objects.create(device=self.device, name="g").privileges, [])

    def test_unique_per_device(self):
        DeviceAccessGroup.objects.create(device=self.device, name="readonly")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DeviceAccessGroup.objects.create(device=self.device, name="readonly")

    def test_same_name_on_another_device(self):
        DeviceAccessGroup.objects.create(device=self.device, name="readonly")
        DeviceAccessGroup.objects.create(device=create_test_device("fw2"), name="readonly").full_clean()

    def test_name_rule(self):
        for bad in ("has space", "x" * 33, "semi;colon"):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                DeviceAccessGroup(device=self.device, name=bad).full_clean()


class DeviceLocalAccountModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("fw1")
        cls.other = create_test_device("fw2")
        cls.group = DeviceAccessGroup.objects.create(device=cls.device, name="readonly")
        cls.foreign_group = DeviceAccessGroup.objects.create(device=cls.other, name="readonly")

    def account(self, **kw):
        return DeviceLocalAccount(**{"device": self.device, "name": "readonly", "group": self.group, **kw})

    def test_create_defaults_str_url(self):
        a = self.account()
        a.full_clean()
        a.save()
        self.assertTrue(a.enabled)
        self.assertFalse(a.api_key)
        self.assertEqual(a.secret_ref, "")
        self.assertEqual(str(a), f"{self.device}: readonly")
        self.assertIn("/plugins/system-services/device-local-accounts/", a.get_absolute_url())

    def test_api_key_with_tier_leaf(self):
        for leaf in ("readonly", "write"):
            with self.subTest(leaf=leaf):
                self.account(api_key=True, secret_ref=f"prod/boden/infra/hq/hq-opnsense/{leaf}").full_clean()

    def test_api_key_needs_secret_ref(self):
        with self.assertRaises(ValidationError) as cm:
            self.account(api_key=True).full_clean()
        self.assertIn("secret_ref", cm.exception.message_dict)

    def test_secret_ref_leaf_must_be_a_tier(self):
        with self.assertRaises(ValidationError) as cm:
            self.account(api_key=True, secret_ref="prod/boden/infra/hq/hq-opnsense/root").full_clean()
        self.assertIn("secret_ref", cm.exception.message_dict)

    def test_secret_ref_shape(self):
        for bad in ("/prod/x/readonly", "prod/x/readonly/", "prod//readonly", "Prod/x/readonly",
                    "prod/../readonly", "prod/x y/readonly"):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                self.account(api_key=True, secret_ref=bad).full_clean()

    def test_group_must_be_on_the_same_device(self):
        with self.assertRaises(ValidationError) as cm:
            self.account(group=self.foreign_group).full_clean()
        self.assertIn("group", cm.exception.message_dict)

    def test_unique_per_device(self):
        self.account().save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.account().save()

    def test_group_with_members_is_protected(self):
        self.account().save()
        with self.assertRaises(RestrictedError):
            self.group.delete()

    def test_device_delete_cascades(self):
        self.account().save()
        self.device.delete()
        self.assertFalse(DeviceLocalAccount.objects.exists())
        self.assertFalse(DeviceAccessGroup.objects.filter(name="readonly", device__name="fw1").exists())


_CRUD = (
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
)


class _PluginAPI:
    view_namespace = "plugins-api:netbox_system_services"


class DeviceAccessGroupAPITest(_PluginAPI, *_CRUD):
    model = DeviceAccessGroup
    brief_fields = ["device", "display", "id", "name", "url"]
    bulk_update_data = {"description": "bulk"}

    @classmethod
    def setUpTestData(cls):
        d = create_test_device("fw-api")
        DeviceAccessGroup.objects.bulk_create([DeviceAccessGroup(device=d, name=f"g{i}") for i in range(3)])
        cls.create_data = [
            {"device": d.pk, "name": "readonly", "privileges": ["page-all", "user-config-readonly"]},
            {"device": d.pk, "name": "iac", "privileges": ["page-all"]},
            {"device": d.pk, "name": "empty"},
        ]


class DeviceLocalAccountAPITest(_PluginAPI, *_CRUD):
    model = DeviceLocalAccount
    brief_fields = ["device", "display", "id", "name", "url"]
    bulk_update_data = {"description": "bulk"}

    @classmethod
    def setUpTestData(cls):
        d = create_test_device("fw-api")
        g = DeviceAccessGroup.objects.create(device=d, name="readonly")
        DeviceLocalAccount.objects.bulk_create([DeviceLocalAccount(device=d, name=f"u{i}", group=g) for i in range(3)])
        cls.create_data = [
            {"device": d.pk, "name": "readonly", "group": g.pk, "api_key": True, "secret_ref": REF},
            {"device": d.pk, "name": "audit", "group": g.pk, "enabled": False},
            {"device": d.pk, "name": "plain", "group": g.pk},
        ]

    def test_api_rejects_key_without_secret_ref(self):
        self.add_permissions("netbox_system_services.add_devicelocalaccount")
        g = DeviceAccessGroup.objects.get(name="readonly")
        r = self.client.post(self._get_list_url(), {"device": g.device_id, "name": "nokey", "group": g.pk,
                                                    "api_key": True}, format="json", **self.header)
        self.assertEqual(r.status_code, 400)
        self.assertIn("secret_ref", r.data)
