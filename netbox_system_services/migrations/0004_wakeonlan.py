# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_system_services --check --dry-run   (on a dev/ephemeral NetBox)
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


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("netbox_system_services", "0003_hostmemoryconfig"),
    ]
    operations = [
        migrations.CreateModel(
            name="WakeOnLanConfig",
            fields=[
                *_BASE,
                ("enabled", models.BooleanField(default=False)),
                ("mode", models.CharField(default="g", max_length=10)),
                ("is_waker", models.BooleanField(default=False)),
                ("interface", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="dcim.interface")),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="wake_on_lan_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "Wake-on-LAN Config", "ordering": ["device"]},
        ),
        migrations.CreateModel(
            name="WakeOnLanTarget",
            fields=[
                *_BASE,
                ("target_device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to="dcim.device")),
                ("config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="targets", to="netbox_system_services.wakeonlanconfig")),
                _TAGS,
            ],
            options={
                "verbose_name": "Wake-on-LAN Target",
                "ordering": ["config", "target_device"],
                "constraints": [models.UniqueConstraint(fields=("config", "target_device"), name="netbox_system_services_wakeonlantarget_unique_config_target")],
            },
        ),
    ]
