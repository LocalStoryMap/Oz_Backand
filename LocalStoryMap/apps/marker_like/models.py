from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from apps.users.models import User


class MarkerLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="marker_likes",
        verbose_name="사용자",
    )
    marker = models.ForeignKey(
        "marker.Marker",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="마커",
    )
    is_liked = models.BooleanField(
        default=False,
        verbose_name="좋아요 여부",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시",
    )

    class Meta:
        db_table = "marker_likes"
        verbose_name = "마커 좋아요"
        verbose_name_plural = "마커 좋아요들"
        unique_together = [("user", "marker")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.marker.marker_name} ({'ON' if self.is_liked else 'OFF'})"
