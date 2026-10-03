# SPDX-License-Identifier: AGPL-3.0-or-later
# Brings migration state in line with the models under NetBox 4.6: NetBoxModel's custom_field_data
# uses utilities.json.CustomFieldJSONEncoder (0006/0008 recorded DjangoJSONEncoder), and
# SystemConfig.fqdn's field definition (0007) differs from the model. Schema-neutral for Postgres.
from django.db import migrations, models
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_system_services", "0010_device_custom_fields_to_systemconfig"),
    ]

    operations = [
        migrations.AlterField(
            model_name="devicecliline",
            name="custom_field_data",
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name="dnshostalias",
            name="custom_field_data",
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name="dnsmasqhost",
            name="custom_field_data",
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AlterField(
            model_name="systemconfig",
            name="fqdn",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
