# Generated by Django 5.2.1 on 2025-06-13 10:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SearchHistory",
        ),
    ]
