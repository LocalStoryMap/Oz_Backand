# Generated by Django 5.2.1 on 2025-06-09 06:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscribe",
            fields=[
                (
                    "subscribe_id",
                    models.BigAutoField(
                        help_text="구독 고유 ID", primary_key=True, serialize=False
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=False, help_text="현재 구독 유효 여부"),
                ),
                (
                    "start_at",
                    models.DateTimeField(auto_now_add=True, help_text="구독 시작일"),
                ),
                (
                    "expires_at",
                    models.DateTimeField(blank=True, help_text="구독 만료일", null=True),
                ),
                (
                    "imp_uid",
                    models.CharField(
                        help_text="아임포트 imp_uid", max_length=255, unique=True
                    ),
                ),
                (
                    "merchant_uid",
                    models.CharField(
                        help_text="아임포트 merchant_uid", max_length=100, unique=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="구독한 사용자",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "구독",
                "verbose_name_plural": "구독 목록",
                "db_table": "Subscribe",
            },
        ),
    ]
