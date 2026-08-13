# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_system_services", "0006_ssh_proxy_dns_cli"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="fqdn",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Fully qualified domain name. The leftmost label is the system hostname; "
                    "the remainder is the domain. When blank, device.name is used as hostname "
                    "with no domain. Decoupled from device.name so Bao secret paths "
                    "(keyed on device.name) remain stable."
                ),
                max_length=255,
            ),
        ),
    ]
