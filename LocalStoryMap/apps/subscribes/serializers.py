import logging
from typing import Any, Dict

from rest_framework import serializers

from .models import Subscribe
from .services.payment import PaymentService, PaymentVerificationError

logger = logging.getLogger(__name__)


class SubscribeInputSerializer(serializers.Serializer):
    """구독 생성 입력 스펙"""

    imp_uid = serializers.CharField(max_length=255)
    merchant_uid = serializers.CharField(max_length=100)

    def validate(self, data: Dict[str, str]) -> Dict[str, Any]:
        """입력 데이터 검증"""
        try:
            # 결제 검증 (Service Layer 사용)
            payment_service = PaymentService()
            payment_result = payment_service.verify_payment(
                imp_uid=data["imp_uid"],
                merchant_uid=data["merchant_uid"],
                user_id=self.context["request"].user.id,
            )

            # 검증된 결제 정보를 validated_data에 추가
            return {
                "imp_uid": payment_result.imp_uid,
                "merchant_uid": payment_result.merchant_uid,
                "payment": payment_result.raw_data,
            }

        except PaymentVerificationError as e:
            raise serializers.ValidationError(str(e))


class SubscribeSerializer(serializers.ModelSerializer):
    """구독 조회 응답 스펙"""

    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Subscribe
        fields = [
            "subscribe_id",
            "user_id",
            "is_active",
            "start_at",
            "expires_at",
            "imp_uid",
            "merchant_uid",
        ]
        read_only_fields = [
            "subscribe_id",
            "user_id",
            "is_active",
            "start_at",
            "expires_at",
        ]
