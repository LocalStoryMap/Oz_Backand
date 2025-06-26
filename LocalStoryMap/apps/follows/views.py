from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import Notification, NotificationSetting
from apps.notifications.serializers import NotificationSettingSerializer

from .models import Follow
from .serializers import FollowCreateSerializer, FollowSerializer


class FollowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET    /api/follows/      : 내 팔로우 목록 조회
    POST   /api/follows/      : 특정 사용자 팔로우 (테스트용 익명 허용)
    DELETE /api/follows/{pk}/ : 언팔로우
    """

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_permissions(self):
        if self.action in ("list", "create", "destroy"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            try:
                user = get_user_model().objects.get(pk=4)
            except get_user_model().DoesNotExist:
                return Follow.objects.none()
        return Follow.objects.filter(follower=user)

    def get_serializer_class(self):
        if self.action == "create":
            return FollowCreateSerializer
        return FollowSerializer

    @swagger_auto_schema(
        tags=["follows"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="팔로우할 사용자의 닉네임",
                ),
            },
            required=["nickname"],
        ),
        responses={201: FollowSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """
        요청 예시:
        {
          "nickname": "닉네임"
        }
        """
        # 1) 팔로우 생성
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        follow = serializer.save(follower=request.user)

        # 2) 알림 설정 확인
        try:
            setting = NotificationSetting.objects.get(
                user=follow.followed,
                type=Notification.FOLLOW,
            )
        except NotificationSetting.DoesNotExist:
            setting = None

        if setting and setting.enabled:
            # 3) Notification 기록 생성
            notification = Notification.objects.create(
                sender=follow.follower,
                receiver=follow.followed,
                type=Notification.FOLLOW,
                target_id=follow.id,
            )
            # 4) WebSocket 푸시
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{follow.followed.id}",
                {
                    "type": "notify",
                    "data": NotificationSettingSerializer(notification).data,
                },
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
