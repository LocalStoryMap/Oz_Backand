import logging
from typing import Any, Dict

from rest_framework import serializers

from .models import Subscribe

logger = logging.getLogger(__name__)


class SubscribeSerializer(serializers.ModelSerializer):
    """구독 시리얼라이저"""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Subscribe
        fields = [
            "id",
            "user",
            "user_email",
            "payment_history_id",
            "expires_at",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "payment_history_id",
            "expires_at",
            "is_active",
            "created_at",
            "updated_at",
        ]


class SubscribeCreateSerializer(serializers.Serializer):
    """구독 생성 요청 시리얼라이저"""

    imp_uid = serializers.CharField()
    merchant_uid = serializers.CharField()
