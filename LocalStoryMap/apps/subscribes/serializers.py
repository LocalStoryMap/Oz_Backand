from typing import Any, Dict

import requests
from django.conf import settings
from rest_framework import serializers

from .models import Subscribe


class SubscribeInputSerializer(serializers.Serializer):

    # POST /subscribes/ 입력 스펙
    # imp_uid · merchant_uid 검증 포함


    imp_uid: str = serializers.CharField(max_length=255)
    merchant_uid: str = serializers.CharField(max_length=100)

    def validate(self, data: Dict[str, str]) -> Dict[str, str]:
        imp_uid: str = data["imp_uid"]
        merchant_uid: str = data["merchant_uid"]

        # 1) 토큰 발급
        token_resp = requests.post(
            "https://api.iamport.kr/users/getToken",
            json={
                "imp_key": settings.IMP_KEY,
                "imp_secret": settings.IMP_SECRET,
            },
        )
        token_resp.raise_for_status()
        access_token: str = token_resp.json()["response"]["access_token"]

        # 2) 결제 내역 조회
        pay_resp = requests.get(
            f"https://api.iamport.kr/payments/{imp_uid}",
            headers={"Authorization": access_token},
        )
        pay_resp.raise_for_status()
        payment: Dict[str, Any] = pay_resp.json()["response"]

        # 3) 금액 검증
        amount: int = int(payment.get("amount", 0))
        if amount != settings.SINGLE_PLAN_PRICE:
            raise serializers.ValidationError(
                {
                    "imp_uid": f"결제 금액 불일치 (기대: {settings.SINGLE_PLAN_PRICE}, 실제: {amount})"
                }
            )

        # 4) merchant_uid 검증
        if payment.get("merchant_uid") != merchant_uid:
            raise serializers.ValidationError({"merchant_uid": "merchant_uid 불일치"})

        return data


class SubscribeSerializer(serializers.ModelSerializer):

    # GET 응답 스펙

    user_id: int = serializers.IntegerField(source="user.id", read_only=True)

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
