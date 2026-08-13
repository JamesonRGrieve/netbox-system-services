# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_system_services --check --dry-run   (on a dev/ephemeral NetBox)
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


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("netbox_system_services", "0002_dnsforwardzone_systemtunable_dynamicdnsrecord"),
    ]
    operations = [
        migrations.CreateModel(
            name="HostMemoryConfig",
            fields=[
                *_BASE,
                ("swappiness", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(200)])),
                ("swap_file_size_mb", models.PositiveIntegerField(blank=True, null=True)),
                ("zram_percent", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)])),
                ("zram_size_mb", models.PositiveIntegerField(blank=True, null=True)),
                ("zram_algorithm", models.CharField(blank=True, max_length=20)),
                ("zram_priority", models.SmallIntegerField(blank=True, null=True)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="host_memory_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "Host Memory Config", "ordering": ["device"]},
        ),
    ]
