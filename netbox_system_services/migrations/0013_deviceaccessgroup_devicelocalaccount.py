# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_system_services --check --dry-run   (on a dev/ephemeral NetBox)
import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

_BASE = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
    ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
    ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
    ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
]
_TAGS = ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"))
_NAME = django.core.validators.RegexValidator(
    "^[a-zA-Z0-9._-]{1,32}$", "1-32 letters, digits, '.', '-' or '_' (the OPNsense user/group name rule)."
)


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("netbox_system_services", "0012_systemconfig_config_history_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceAccessGroup",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=32, validators=[_NAME])),
                ("privileges", django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=128), blank=True, default=list,
                    help_text="Device privilege ids, e.g. page-all, user-config-readonly.", size=None)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="access_groups", to="dcim.device")),
                _TAGS,
            ],
            options={
                "verbose_name": "Device Access Group",
                "ordering": ["device", "name"],
                "constraints": [models.UniqueConstraint(fields=("device", "name"), name="netbox_system_services_deviceaccessgroup_unique_device_name")],
            },
        ),
        migrations.CreateModel(
            name="DeviceLocalAccount",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=32, validators=[_NAME])),
                ("enabled", models.BooleanField(default=True)),
                ("api_key", models.BooleanField(default=False, help_text="The pipeline mints this account one API key, filed at secret_ref.")),
                ("secret_ref", models.CharField(blank=True, max_length=255, help_text="OpenBao KV path the minted key is filed at, e.g. prod/boden/infra/hq/hq-opnsense/readonly. NEVER the key itself.")),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="local_accounts", to="dcim.device")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="members", to="netbox_system_services.deviceaccessgroup")),
                _TAGS,
            ],
            options={
                "verbose_name": "Device Local Account",
                "ordering": ["device", "name"],
                "constraints": [models.UniqueConstraint(fields=("device", "name"), name="netbox_system_services_devicelocalaccount_unique_device_name")],
            },
        ),
    ]
