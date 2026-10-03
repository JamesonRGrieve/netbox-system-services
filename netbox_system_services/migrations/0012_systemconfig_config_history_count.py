# SPDX-License-Identifier: AGPL-3.0-or-later
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_system_services", "0011_netbox46_custom_field_encoder_and_fqdn"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="config_history_count",
            field=models.PositiveIntegerField(
                blank=True, null=True,
                help_text="Configuration revisions the device keeps (OPNsense <system><backupcount>). "
                          "Blank = leave the device default (100 on OPNsense). 0 is rejected: OPNsense "
                          "would delete every saved revision.",
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
