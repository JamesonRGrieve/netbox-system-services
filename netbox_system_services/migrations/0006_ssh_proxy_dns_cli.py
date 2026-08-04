# SPDX-License-Identifier: AGPL-3.0-or-later
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0001_initial"),
        ("netbox_system_services", "0005_systemconfig_ssh_syslog_filter"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_proxy_host",
            field=models.CharField(blank=True, default="", max_length=255, help_text="SSH ProxyJump host (empty = direct connection)."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_proxy_port",
            field=models.PositiveIntegerField(default=22, help_text="SSH ProxyJump port."),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_proxy_user",
            field=models.CharField(blank=True, default="", max_length=128, help_text="SSH ProxyJump user."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_proxy_identity",
            field=models.CharField(blank=True, default="", max_length=255, help_text="OpenBao KV path for the ProxyJump private key."),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="DnsHostAlias",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("hostname", models.CharField(max_length=255, help_text="FQDN or short hostname to override.")),
                ("target", models.GenericIPAddressField(help_text="IP address the hostname resolves to.")),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dns_host_aliases", to="dcim.device")),
            ],
            options={
                "ordering": ["device", "hostname"],
                "verbose_name": "DNS Host Alias",
                "verbose_name_plural": "DNS Host Aliases",
            },
        ),
        migrations.AddConstraint(
            model_name="dnshostalias",
            constraint=models.UniqueConstraint(fields=("device", "hostname"), name="netbox_system_services_dnshostalias_unique_device_hostname"),
        ),
        migrations.CreateModel(
            name="DnsmasqHost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("hostname", models.CharField(max_length=255, help_text="Hostname for the dnsmasq host record.")),
                ("ip_address", models.GenericIPAddressField(help_text="IP address for the host record.")),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dnsmasq_hosts", to="dcim.device")),
            ],
            options={
                "ordering": ["device", "hostname"],
                "verbose_name": "Dnsmasq Host",
            },
        ),
        migrations.AddConstraint(
            model_name="dnsmasqhost",
            constraint=models.UniqueConstraint(fields=("device", "hostname"), name="netbox_system_services_dnsmasqhost_unique_device_hostname"),
        ),
        migrations.CreateModel(
            name="DeviceCLILine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("line", models.TextField(help_text="Raw CLI line to include in the device config.")),
                ("weight", models.PositiveIntegerField(default=100, help_text="Ordering weight (lower = earlier).")),
                ("description", models.CharField(blank=True, max_length=200)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cli_lines", to="dcim.device")),
            ],
            options={
                "ordering": ["device", "weight"],
                "verbose_name": "Device CLI Line",
            },
        ),
    ]
