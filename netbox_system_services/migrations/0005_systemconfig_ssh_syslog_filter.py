# SPDX-License-Identifier: AGPL-3.0-or-later
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_system_services", "0004_wakeonlan"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_port",
            field=models.PositiveIntegerField(default=22, help_text="SSHd listen port."),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_password_auth",
            field=models.BooleanField(default=True, help_text="Allow SSH password authentication."),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="ssh_allow_users",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128),
                default=list,
                blank=True,
                help_text="SSHd AllowUsers list (empty = unrestricted).",
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="syslogconfig",
            name="filter_string",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Syslog filter expression (platform-specific, e.g. rsyslog property-based filter).",
            ),
            preserve_default=False,
        ),
    ]
