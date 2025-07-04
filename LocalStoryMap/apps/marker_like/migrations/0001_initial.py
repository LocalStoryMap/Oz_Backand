# Generated by Django 5.2.1 on 2025-06-17 02:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("marker", "0005_marker_like_count"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MarkerLike",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_liked", models.BooleanField(default=False, verbose_name="좋아요 여부")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성일시"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="수정일시"),
                ),
                (
                    "marker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="marker.marker",
                        verbose_name="마커",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="marker_likes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "마커 좋아요",
                "verbose_name_plural": "마커 좋아요들",
                "db_table": "marker_likes",
                "ordering": ["-created_at"],
                "unique_together": {("user", "marker")},
            },
        ),
    ]
