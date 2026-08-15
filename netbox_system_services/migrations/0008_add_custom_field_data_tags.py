# SPDX-License-Identifier: AGPL-3.0-or-later
import django.core.serializers.json
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0001_initial"),
        ("netbox_system_services", "0007_systemconfig_fqdn"),
    ]

    operations = [
        migrations.AddField(
            model_name="devicecliline",
            name="custom_field_data",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
            ),
        ),
        migrations.AddField(
            model_name="devicecliline",
            name="tags",
            field=taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AddField(
            model_name="dnshostalias",
            name="custom_field_data",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
            ),
        ),
        migrations.AddField(
            model_name="dnshostalias",
            name="tags",
            field=taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AddField(
            model_name="dnsmasqhost",
            name="custom_field_data",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
            ),
        ),
        migrations.AddField(
            model_name="dnsmasqhost",
            name="tags",
            field=taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"),
        ),
    ]
