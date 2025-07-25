# Generated by Django 5.0.9 on 2025-05-29 11:47

import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0071_rename_domain_hash_to_linked_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="linkeddomain",
            name="state",
            field=models.CharField(
                choices=[
                    ("Pending review", "Pending Review"),
                    ("Approved", "Approved"),
                ],
                default="Pending review",
                max_length=255,
            ),
        ),
    ]
