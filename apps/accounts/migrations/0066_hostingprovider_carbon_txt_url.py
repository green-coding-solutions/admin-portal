# Generated by Django 5.0.9 on 2025-04-07 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0065_create_domain_hash"),
    ]

    operations = [
        migrations.AddField(
            model_name="hostingprovider",
            name="carbon_txt_url",
            field=models.URLField(max_length=255, null=True),
        ),
    ]
