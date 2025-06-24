from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

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

    # 기본적으로 로그인 필요
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # create 액션만 무조건 익명 허용 (테스트용)
        if self.action in ("list", "create", "destroy"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        # create 시엔 FollowCreateSerializer, 그 외에는 FollowSerializer
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
        return super().create(request, *args, **kwargs)
