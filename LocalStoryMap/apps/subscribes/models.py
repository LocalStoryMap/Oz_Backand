from datetime import datetime, timedelta
from typing import Optional

from django.db import models

from apps.users.models import User


class Subscribe(models.Model):

    subscribe_id: int = models.BigAutoField(primary_key=True, help_text="구독 고유 ID")
    user: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text="구독한 사용자",
    )
    is_active: bool = models.BooleanField(default=False, help_text="현재 구독 유효 여부")
    start_at: datetime = models.DateTimeField(auto_now_add=True, help_text="구독 시작일")
    expires_at: Optional[datetime] = models.DateTimeField(
        null=True, blank=True, help_text="구독 만료일"
    )
    imp_uid: str = models.CharField(
        max_length=255, unique=True, help_text="아임포트 imp_uid"
    )
    merchant_uid: str = models.CharField(
        max_length=100, unique=True, help_text="아임포트 merchant_uid"
    )

    class Meta:
        db_table = "Subscribe"
        verbose_name = "구독"
        verbose_name_plural = "구독 목록"

    def __str__(self) -> str:
        status: str = "활성" if self.is_active else "만료"
        return f"#{self.subscribe_id} – {self.user} ({status})"
