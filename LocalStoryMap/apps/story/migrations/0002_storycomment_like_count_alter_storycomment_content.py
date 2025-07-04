# Generated by Django 5.2.1 on 2025-06-17 08:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("story", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="storycomment",
            name="like_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="storycomment",
            name="content",
            field=models.TextField(verbose_name="댓글 내용"),
        ),
    ]
