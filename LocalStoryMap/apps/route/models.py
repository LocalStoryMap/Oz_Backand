from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() # 임시 유저

class Route(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='routes',
        verbose_name='작성자'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='경로명'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='경로 설명'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'routes'
        verbose_name = '경로'
        verbose_name_plural = '경로들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.user.username})"

    @property
    def marker_count(self):
        # 연결된 마커 수
        return self.route_markers.count()

    def get_ordered_markers(self):
        # 순서대로 정렬된 마커들 반환
        return self.route_markers.select_related('marker').order_by('sequence')
