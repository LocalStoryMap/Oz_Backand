from django.db import models

from apps.users.models import User


class RouteLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="route_likes",
        verbose_name="사용자",
    )
    route = models.ForeignKey(
        "route.Route",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="경로",
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
        db_table = "route_likes"
        verbose_name = "경로 좋아요"
        verbose_name_plural = "경로 좋아요들"
        unique_together = [("user", "route")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.route.name} ({'ON' if self.is_liked else 'OFF'})"
