from django.db import models
from django.db.models import F

from apps.users.models import User


class Route(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="routes",
        verbose_name="작성자",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="경로명",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="경로 설명",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="공개여부",
    )
    like_count = models.PositiveIntegerField(
        default=0,
        verbose_name="경로 좋아요 수",
    )

    class Meta:
        db_table = "routes"
        verbose_name = "경로"
        verbose_name_plural = "경로들"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

    @property
    def marker_count(self):
        # 연결된 마커 수
        return self.route_markers.count()

    def get_ordered_markers(self):
        # 순서대로 정렬된 마커들 반환
        return self.route_markers.select_related("marker").order_by("sequence")

    def increment_like_count(self):
        # 좋아요 수 증가
        self.like_count = F('like_count') + 1
        self.save(update_fields=['like_count'])
        self.refresh_from_db()

    def decrement_like_count(self):
        # 좋아요 수 감소
        if self.like_count > 0:
            self.like_count = F('like_count') - 1
            self.save(update_fields=['like_count'])
            self.refresh_from_db()