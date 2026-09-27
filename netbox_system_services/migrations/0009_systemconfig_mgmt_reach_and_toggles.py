# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored additive migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_system_services --check --dry-run
#
# Moves the per-device management-reach and subsystem-toggle custom fields onto SystemConfig,
# which already owns ssh_port / ssh_password_auth / ssh_proxy_* — so the device's SSH story stops
# being split between a real model and a JSON column. 0010 copies the existing values across.
#
# Defaults mirror what each consumer's lookup() default was, so a device with no value behaves
# exactly as it does today. manage_interface_baseline defaults FALSE on purpose: enabling it on an
# already-deployed multi-VLAN box re-runs a 3-NIC bringup over live interface assignments.
from django.db import migrations, models


def _char(**kw):
    return models.CharField(blank=True, **kw)


class Migration(migrations.Migration):
    dependencies = [("netbox_system_services", "0008_add_custom_field_data_tags")]

    operations = [
        migrations.AddField("systemconfig", "ssh_host", _char(max_length=255)),
        migrations.AddField("systemconfig", "ssh_user", _char(max_length=128)),
        migrations.AddField("systemconfig", "ssh_identity", _char(max_length=255)),
        migrations.AddField("systemconfig", "login_banner", models.TextField(blank=True)),
        migrations.AddField("systemconfig", "manage_interface_baseline",
                            models.BooleanField(default=False)),
        migrations.AddField("systemconfig", "manage_base_lan", models.BooleanField(default=False)),
        migrations.AddField("systemconfig", "manage_lan", models.BooleanField(default=True)),
        migrations.AddField("systemconfig", "manage_timezone", models.BooleanField(default=True)),
        migrations.AddField("systemconfig", "manage_reconcile", models.BooleanField(default=True)),
        migrations.AddField("systemconfig", "manage_plugin_aliases",
                            models.BooleanField(default=True)),
        migrations.AddField("systemconfig", "wan_proto", _char(max_length=32)),
        migrations.AddField("systemconfig", "lan_if", _char(max_length=64)),
        migrations.AddField("systemconfig", "vlan_trunk", _char(max_length=64)),
        migrations.AddField("systemconfig", "vlanif_pfstyle", models.BooleanField(default=False)),
        migrations.AddField("systemconfig", "openwrt_native_dsa",
                            models.BooleanField(default=False)),
        migrations.AddField("systemconfig", "openwrt_network_reload",
                            models.BooleanField(default=True)),
        migrations.AddField("systemconfig", "dhcp_engine", _char(max_length=32)),
        migrations.AddField("systemconfig", "haproxy_setpath_separate_type",
                            models.BooleanField(default=False)),
    ]
