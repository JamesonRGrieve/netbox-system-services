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
        ("netbox_system_services", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DnsForwardZone",
            fields=[
                *_BASE,
                ("domain", models.CharField(max_length=255)),
                ("server", models.GenericIPAddressField()),
                ("port", models.PositiveSmallIntegerField(default=53)),
                ("backend", models.CharField(default="unbound", max_length=16)),
                ("tcp_upstream", models.BooleanField(default=False)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dns_forward_zones", to="dcim.device")),
                _TAGS,
            ],
            options={
                "verbose_name": "DNS Forward Zone",
                "ordering": ["device", "domain", "server"],
                "constraints": [models.UniqueConstraint(fields=("device", "domain", "server"), name="netbox_system_services_dnsforwardzone_unique_device_domain_server")],
            },
        ),
        migrations.CreateModel(
            name="SystemTunable",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=255)),
                ("value", models.CharField(max_length=255)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="system_tunables", to="dcim.device")),
                _TAGS,
            ],
            options={
                "verbose_name": "System Tunable",
                "ordering": ["device", "name"],
                "constraints": [models.UniqueConstraint(fields=("device", "name"), name="netbox_system_services_systemtunable_unique_device_name")],
            },
        ),
        migrations.CreateModel(
            name="DynamicDNSRecord",
            fields=[
                *_BASE,
                ("fqdn", models.CharField(max_length=255)),
                ("zone", models.CharField(blank=True, max_length=255)),
                ("service", models.CharField(default="cloudflare", max_length=32)),
                ("credential_ref", models.CharField(blank=True, max_length=255)),
                ("check_ip_method", models.CharField(blank=True, default="web", max_length=64)),
                ("enabled", models.BooleanField(default=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dynamic_dns_records", to="dcim.device")),
                _TAGS,
            ],
            options={
                "verbose_name": "Dynamic DNS Record",
                "ordering": ["device", "fqdn"],
                "constraints": [models.UniqueConstraint(fields=("device", "fqdn"), name="netbox_system_services_dynamicdnsrecord_unique_device_fqdn")],
            },
        ),
    ]
