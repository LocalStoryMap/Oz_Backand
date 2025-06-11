from django.db import models, transaction


class RouteMarker(models.Model):
    route = models.ForeignKey(
        "route.Route",
        on_delete=models.CASCADE,
        related_name="route_markers",
        verbose_name="경로",
    )
    marker = models.ForeignKey(
        "marker.Marker",
        on_delete=models.CASCADE,
        related_name="route_markers",
        verbose_name="마커",
    )
    sequence = models.PositiveIntegerField(
        verbose_name="순서",
        help_text="경로 내에서의 마커 순서 (1부터 시작)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="연결일시",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시",
    )

    class Meta:
        db_table = "route_markers"
        verbose_name = "경로-마커 연결"
        verbose_name_plural = "경로-마커 연결들"
        unique_together = [
            ("route", "marker"),  # 같은 경로에 같은 마커 중복 방지
            ("route", "sequence"),  # 같은 경로에 같은 순서 중복 방지
        ]
        ordering = ["route", "sequence"]

    def __str__(self):
        return f"{self.route.name} - {self.marker.marker_name} ({self.sequence})"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_next_sequence(cls, route):
        # 해당 경로의 다음 순서 번호 반환
        last_sequence = cls.objects.filter(route=route).aggregate(
            max_seq=models.Max("sequence")
        )["max_seq"]
        return (last_sequence or 0) + 1

    @classmethod
    def reorder_sequence(cls, route, new_order_list):
        # 경로의 마커 순서를 일괄 변경
        # new_order_list: [(route_marker_id, new_sequence), ...]
        with transaction.atomic():
            existing_connections = cls.objects.select_for_update().filter(route=route)

            temp_offset = existing_connections.count() + 10000

            for conn in existing_connections:
                conn.sequence += temp_offset
                conn.save(update_fields=["sequence"])

            for route_marker_id, new_sequence in new_order_list:
                cls.objects.filter(id=route_marker_id, route=route).update(
                    sequence=new_sequence
                )
