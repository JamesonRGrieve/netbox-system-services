# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_system_services --check --dry-run   (on a dev/ephemeral NetBox)
import django.contrib.postgres.fields
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
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="SystemConfig",
            fields=[
                *_BASE,
                ("default_gateway", models.GenericIPAddressField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("contact", models.CharField(blank=True, max_length=255)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="system_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "System Config", "ordering": ["device"]},
        ),
        migrations.CreateModel(
            name="SNMPConfig",
            fields=[
                *_BASE,
                ("enabled", models.BooleanField(default=True)),
                ("listen_interface", models.CharField(blank=True, max_length=128)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="snmp_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "SNMP Config", "ordering": ["device"]},
        ),
        migrations.CreateModel(
            name="SNMPCommunity",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=128)),
                ("access", models.CharField(default="ro", max_length=2)),
                ("restricted", models.BooleanField(default=False)),
                ("snmp_config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="communities", to="netbox_system_services.snmpconfig")),
                _TAGS,
            ],
            options={
                "verbose_name": "SNMP Community",
                "verbose_name_plural": "SNMP Communities",
                "ordering": ["snmp_config", "name"],
                "constraints": [models.UniqueConstraint(fields=("snmp_config", "name"), name="netbox_system_services_snmpcommunity_unique_config_name")],
            },
        ),
        migrations.CreateModel(
            name="SNMPTrapTarget",
            fields=[
                *_BASE,
                ("target", models.GenericIPAddressField()),
                ("port", models.PositiveIntegerField(default=162)),
                ("version", models.CharField(default="v2c", max_length=4)),
                ("community_ref", models.CharField(blank=True, max_length=128)),
                ("snmp_config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trap_targets", to="netbox_system_services.snmpconfig")),
                _TAGS,
            ],
            options={"verbose_name": "SNMP Trap Target", "ordering": ["snmp_config", "target", "port"]},
        ),
        migrations.CreateModel(
            name="SyslogConfig",
            fields=[
                *_BASE,
                ("severity", models.CharField(default="info", max_length=8)),
                ("facility", models.CharField(default="user", max_length=8)),
                ("retention_days", models.PositiveIntegerField(default=7)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="syslog_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "Syslog Config", "ordering": ["device"]},
        ),
        migrations.CreateModel(
            name="SyslogServer",
            fields=[
                *_BASE,
                ("host", models.GenericIPAddressField()),
                ("port", models.PositiveIntegerField(default=514)),
                ("transport", models.CharField(default="udp", max_length=4)),
                ("syslog_config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="servers", to="netbox_system_services.syslogconfig")),
                _TAGS,
            ],
            options={"verbose_name": "Syslog Server", "ordering": ["syslog_config", "host", "port"]},
        ),
        migrations.CreateModel(
            name="NTPConfig",
            fields=[
                *_BASE,
                ("enabled", models.BooleanField(default=False)),
                ("broadcast", models.BooleanField(default=True)),
                ("serve_lan", models.BooleanField(default=False)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="ntp_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "NTP Config", "ordering": ["device"]},
        ),
        migrations.CreateModel(
            name="NTPServer",
            fields=[
                *_BASE,
                ("host", models.CharField(max_length=255)),
                ("prefer", models.BooleanField(default=False)),
                ("ntp_config", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="servers", to="netbox_system_services.ntpconfig")),
                _TAGS,
            ],
            options={"verbose_name": "NTP Server", "ordering": ["ntp_config", "host"]},
        ),
        migrations.CreateModel(
            name="DNSResolverConfig",
            fields=[
                *_BASE,
                ("mode", models.CharField(default="static", max_length=8)),
                ("nameservers", django.contrib.postgres.fields.ArrayField(base_field=models.GenericIPAddressField(), blank=True, default=list, size=None)),
                ("search_domains", django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None)),
                ("device", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="dns_resolver_config", to="dcim.device")),
                _TAGS,
            ],
            options={"verbose_name": "DNS Resolver Config", "ordering": ["device"]},
        ),
    ]
