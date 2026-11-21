# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_system_services", "0013_deviceaccessgroup_devicelocalaccount"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="allow_unsupported_transceiver",
            field=models.BooleanField(
                default=False,
                help_text="Let the switch bring up third-party optics/DACs it does not recognise "
                          "(AOS-S `allow-unsupported-transceiver`). False = the switch default.",
            ),
        ),
    ]
