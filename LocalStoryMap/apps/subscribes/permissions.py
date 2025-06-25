from django.utils import timezone
from rest_framework.permissions import SAFE_METHODS, BasePermission


class SubscriberPermission(BasePermission):
    """
    1) is_subscriber=True 면 모든 요청 허용
    2) is_subscriber=False 면 스토리 조회(GET, HEAD, OPTIONS) 뷰에서만 허용
    3) 그 외는 모두 403
    """

    message = "구독자 전용 기능이거나, 스토리 조회만 가능합니다."

    def has_permission(self, request, view):
        user = request.user
        # 1) 로그인 확인
        if not user or not user.is_authenticated:
            return False

        # 2) Boolean 필드로 구독 여부 판단
        if getattr(user, "is_subscriber", False):
            return True

        # 3) 비구독자는 SAFE_METHODS & 스토리 조회 뷰만 허용
        if request.method in SAFE_METHODS:
            view_name = view.__class__.__name__
            if view_name in ["StoryListAPIView", "StoryRetrieveAPIView"]:
                return True

        # 4) 그 외는 차단
        return False
