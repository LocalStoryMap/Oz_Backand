from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification

from .models import Follow
from .serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    """
    팔로우 관리
    """

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="팔로우 목록 조회",
        operation_description="현재 사용자가 팔로우한 사용자 목록을 조회합니다.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="팔로우 생성", operation_description="지정된 사용자를 팔로우합니다."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="팔로우 취소", operation_description="지정된 사용자를 언팔로우합니다."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.follower != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Follow.objects.none()
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        # 1) 팔로우 관계 저장
        follow = serializer.save(follower=self.request.user)
        target = follow.target_user

        # 2) 알림(Notification) 저장
        notif = Notification.objects.create(
            sender=self.request.user,
            receiver=target,
            type=Notification.FOLLOW,
            target_id=self.request.user.id,
        )

        # 3) WebSocket 실시간 푸시
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{target.id}",
            {
                "type": "notify",
                "data": {
                    "id": notif.id,
                    "sender": {
                        "id": self.request.user.id,
                        "username": self.request.user.username,
                    },
                    "type": notif.type,
                    "message": f"{self.request.user.username}님이 팔로우했습니다.",
                    "created_at": notif.created_at.isoformat(),
                },
            },
        )
