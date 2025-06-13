from django.db import models


class Marker(models.Model):
    # story = models.ForeignKey(
    # 'apps.Story',
    # on_delete=models.SET_NULL,
    # null=True,
    # blank=True
    # )
    marker_name = models.CharField(
        max_length=100,
        verbose_name="마커명",
    )
    adress = models.TextField(
        blank=True,
        null=True,
        verbose_name="도로명주소 or 지번주소",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="마커 설명",
    )
    image = models.ImageField(
        upload_to="markers/",  # 업로드될 경로 S3 추후 적용
        blank=True,
        null=True,
        verbose_name="마커 이미지",
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="위도",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        verbose_name="경도",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시",
    )
    LAYER_CHOICES = [
        ("tour", "관광명소"),
        ("food", "맛집"),
        ("cafe", "카페"),
    ]
    layer = models.CharField(
        max_length=20, blank=True, null=True, choices=LAYER_CHOICES, verbose_name="레이어"
    )

    class Meta:
        db_table = "markers"
        verbose_name = "마커"
        verbose_name_plural = "마커들"
        ordering = ["-created_at"]

    def __str__(self):
        return self.marker_name

    @property
    def coordinate(self):
        # 좌표를 튜플로 반환
        return (float(self.latitude), float(self.longitude))

    def get_routes(self):
        # 이 마커가 포함된 경로들
        return [rm.route for rm in self.route_markers.select_related("route")]
