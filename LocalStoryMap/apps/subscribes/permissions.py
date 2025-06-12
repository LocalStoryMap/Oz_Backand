from django.utils import timezone
from rest_framework.permissions import BasePermission


class IsActiveSubscriber(BasePermission):
    # 활성 구독 중인 사용자만 접근을 허용합니다.
    message = "활성 구독이 필요합니다."

    def has_permission(self, request, view):
        sub = getattr(request.user, "subscription", None)
        return bool(
            sub and sub.is_active and sub.expires_at and sub.expires_at > timezone.now()
        )
