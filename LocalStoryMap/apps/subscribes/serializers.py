import logging
from typing import Any, Dict

from rest_framework import serializers

from .models import Subscribe

logger = logging.getLogger(__name__)


class SubscribeSerializer(serializers.ModelSerializer):
    """구독 시리얼라이저"""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    is_paid_user = serializers.BooleanField(source="user.is_paid_user", read_only=True)

    class Meta:
        model = Subscribe
        fields = [
            "subscribe_id",
            "user",
            "user_email",
            "imp_uid",  # 결제 고유 ID
            "merchant_uid",  # 가맹점 주문번호
            "is_active",
            "start_at",
            "expires_at",
            "is_paid_user",
        ]
        read_only_fields = [
            "subscribe_id",
            "user",
            "user_email",
            "is_active",
            "start_at",
            "expires_at",
            "is_paid_user",
        ]


class SubscribeCreateSerializer(serializers.Serializer):
    """구독 생성 요청 시리얼라이저"""

    imp_uid = serializers.CharField()
    merchant_uid = serializers.CharField()
