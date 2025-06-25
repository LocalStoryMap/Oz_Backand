from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import NotificationSetting
from .serializers import NotificationSettingSerializer


class NotificationSettingViewSet(viewsets.ModelViewSet):
    """
    알림 설정 CRUD
    """

    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["notifications"],
        operation_summary="알림 설정 목록 조회",
        operation_description="현재 사용자의 알림 설정 목록을 조회합니다.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["notifications"],
        operation_summary="알림 설정 생성/수정",
        operation_description="사용자의 알림 설정을 생성하거나 수정합니다.",
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        setting_type = request.data.get("type")
        enabled = request.data.get("enabled", True)

        # user, type 조합으로 upsert
        instance, created = NotificationSetting.objects.update_or_create(
            user=user, type=setting_type, defaults={"enabled": enabled}
        )

        serializer = self.get_serializer(instance)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        tags=["notifications"],
        operation_summary="알림 설정 상세 조회",
        operation_description="특정 알림 설정의 상세 정보를 조회합니다.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["notifications"],
        operation_summary="알림 설정 수정",
        operation_description="기존 알림 설정을 업데이트합니다.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["notifications"],
        operation_summary="알림 설정 삭제",
        operation_description="특정 알림 설정을 삭제합니다.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return NotificationSetting.objects.filter(user=self.request.user)
