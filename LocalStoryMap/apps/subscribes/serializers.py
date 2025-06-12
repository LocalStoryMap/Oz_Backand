import logging
from typing import Any, Dict, TypedDict, cast

import requests
from django.conf import settings
from rest_framework import serializers, status

from .models import Subscribe

logger = logging.getLogger(__name__)


class PaymentData(TypedDict):
    imp_uid: str
    merchant_uid: str
    payment: Dict[str, Any]


class SubscribeInputSerializer(serializers.Serializer):
    # POST /subscribes/ 입력 스펙
    # imp_uid · merchant_uid 검증 포함

    imp_uid = serializers.CharField(max_length=255)
    merchant_uid = serializers.CharField(max_length=100)

    def validate(self, data: Dict[str, str]) -> PaymentData:
        imp_uid: str = data["imp_uid"]
        merchant_uid: str = data["merchant_uid"]

        try:
            # 1) 토큰 발급
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5,
            )
            token_resp.raise_for_status()
            access_token: str = token_resp.json()["response"]["access_token"]

            # 2) 결제 내역 조회
            pay_resp = requests.get(
                f"https://api.iamport.kr/payments/{imp_uid}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5,
            )
            pay_resp.raise_for_status()
            payment: Dict[str, Any] = pay_resp.json()["response"]

            # 3) 응답 검증
            if payment.get("status") != "paid":
                raise serializers.ValidationError(
                    f"결제가 완료되지 않았습니다. (상태: {payment.get('status')})"
                )

            # 4) 금액 검증
            amount: int = int(payment.get("amount", 0))
            if amount != settings.SINGLE_PLAN_PRICE:
                raise serializers.ValidationError(
                    f"결제 금액이 일치하지 않습니다. (기대: {settings.SINGLE_PLAN_PRICE}, 실제: {amount})"
                )

            # 5) merchant_uid 검증
            if payment.get("merchant_uid") != merchant_uid:
                raise serializers.ValidationError("merchant_uid가 일치하지 않습니다.")

            # 검증된 결제 정보를 validated_data에 추가
            return PaymentData(
                imp_uid=imp_uid,
                merchant_uid=merchant_uid,
                payment=payment,
            )

        except requests.exceptions.Timeout:
            logger.error(f"아임포트 API 타임아웃: imp_uid={imp_uid}")
            raise serializers.ValidationError(
                "결제 검증 중 시간 초과가 발생했습니다.", code="timeout"  # HTTP 상태 코드 대신 문자열 코드 사용
            )
        except requests.exceptions.ConnectionError:
            logger.error(f"아임포트 API 연결 실패: imp_uid={imp_uid}")
            raise serializers.ValidationError(
                "결제 검증 중 연결 오류가 발생했습니다.",
                code="connection_error",  # HTTP 상태 코드 대신 문자열 코드 사용
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"아임포트 API 호출 실패: imp_uid={imp_uid}, error={e}")
            resp = getattr(e, "response", None)
            error_code = "server_error"  # 기본 에러 코드
            if resp is not None and hasattr(resp, "status_code"):
                error_code = f"http_{resp.status_code}"
            raise serializers.ValidationError(
                f"결제 검증 중 오류가 발생했습니다: {e}", code=error_code
            )


class SubscribeSerializer(serializers.ModelSerializer):
    # GET 응답 스펙

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
