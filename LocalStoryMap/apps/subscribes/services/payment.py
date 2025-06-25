import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.paymenthistory.models import PaymentHistory, PaymentStatus
from apps.subscribes.models import Subscribe
from apps.users.models import User

logger = logging.getLogger(__name__)


@dataclass
class PaymentResult:
    """결제 검증 결과"""

    imp_uid: str
    merchant_uid: str
    amount: int
    payment_method: Optional[str]
    card_name: Optional[str]
    card_number: Optional[str]
    paid_at: Optional[datetime]
    receipt_url: Optional[str]
    raw_data: Dict[str, Any]

    @classmethod
    def from_payment(cls, payment: Dict[str, Any]) -> "PaymentResult":
        """포트원 결제 데이터로부터 PaymentResult 생성"""
        return cls(
            imp_uid=payment["imp_uid"],
            merchant_uid=payment["merchant_uid"],
            amount=int(payment["amount"]),
            payment_method=payment.get("pay_method"),
            card_name=payment.get("card_name"),
            card_number=payment.get("card_number"),
            paid_at=payment.get("paid_at"),
            receipt_url=payment.get("receipt_url"),
            raw_data=payment,
        )


class PaymentVerificationError(Exception):
    """결제 검증 실패"""

    pass


class ImpClient:
    """포트원 API 클라이언트"""

    def __init__(self) -> None:
        self.base_url = "https://api.iamport.kr"
        self._access_token: Optional[str] = None

    def _get_token(self) -> str:
        """포트원 API 토큰 발급"""
        if self._access_token:
            return self._access_token

        try:
            resp = requests.post(
                f"{self.base_url}/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5,
            )
            resp.raise_for_status()
            token = resp.json()["response"]["access_token"]
            if not token:
                raise PaymentVerificationError("토큰 발급 실패")
            self._access_token = token
            return token

        except requests.exceptions.RequestException as e:
            logger.error(f"포트원 토큰 발급 실패: {e}")
            raise PaymentVerificationError("결제 검증 중 오류가 발생했습니다.")

    def get_payment(self, imp_uid: str) -> dict[str, Any]:
        """결제 내역 조회"""
        try:
            resp = requests.get(
                f"{self.base_url}/payments/{imp_uid}",
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()["response"]

        except requests.exceptions.RequestException as e:
            logger.error(f"결제 내역 조회 실패: imp_uid={imp_uid}, error={e}")
            raise PaymentVerificationError("결제 내역을 조회하는 중 오류가 발생했습니다.")


class PaymentService:
    """결제 검증 및 처리 서비스"""

    def __init__(self, imp_client: Optional[ImpClient] = None) -> None:
        self.imp_client = imp_client or ImpClient()

    def process_subscription_payment(
        self, imp_uid: str, merchant_uid: str, user_id: int
    ) -> tuple[PaymentResult, Subscribe]:
        """결제 검증 및 구독 생성 (단일 트랜잭션)

        Args:
            imp_uid: 포트원 결제 고유번호
            merchant_uid: 가맹점 주문번호

        Returns:
            tuple[PaymentResult, Subscribe]: (결제 검증 결과, 생성된 구독)

        Raises:
            PaymentVerificationError: 결제 검증 실패
            ValidationError: 구독 생성 실패
        """
        # 1. 결제 내역 조회
        payment = self.imp_client.get_payment(imp_uid)

        # 2. 결제 상태/금액/merchant_uid 검증 (프론트에서 받은 값은 imp_uid, merchant_uid만 사용)
        if payment.get("status") != "paid":
            raise PaymentVerificationError(
                f"결제가 완료되지 않았습니다. (상태: {payment.get('status')})"
            )
        if payment.get("merchant_uid") != merchant_uid:
            raise PaymentVerificationError("merchant_uid가 일치하지 않습니다.")
        # 금액 검증은 포트원에서 조회한 값과 서버 설정값 비교
        amount = int(payment.get("amount", 0))
        if amount != settings.SINGLE_PLAN_PRICE:
            raise PaymentVerificationError(
                f"결제 금액이 일치하지 않습니다. (기대: {settings.SINGLE_PLAN_PRICE}, 실제: {amount})"
            )

        # 3. PaymentResult 생성
        result = PaymentResult.from_payment(payment)

        # 4. 기존 활성 구독 확인
        if Subscribe.objects.filter(user_id=user_id, is_active=True).exists():
            raise ValidationError("이미 활성화된 구독이 있습니다.")

        # 5. 결제 이력 생성
        try:
            payment_history = PaymentHistory.objects.create(
                user_id=user_id,
                imp_uid=result.imp_uid,
                merchant_uid=result.merchant_uid,
                amount=result.amount,
                status=PaymentStatus.PAID,
                payment_method=result.payment_method,
                card_name=result.card_name,
                card_number=result.card_number,
                paid_at=result.paid_at,
                receipt_url=result.receipt_url,
            )
            logger.info(
                f"결제 이력 생성 성공: user_id={user_id}, "
                f"imp_uid={result.imp_uid}, amount={result.amount}"
            )
        except Exception as e:
            logger.error(
                f"결제 이력 생성 실패: user_id={user_id}, "
                f"imp_uid={result.imp_uid}, error={e}"
            )
            raise PaymentVerificationError("결제 이력 생성 중 오류가 발생했습니다.")

        # 6. 구독 생성
        try:
            expires_at = timezone.now() + timedelta(days=30)
            subscription = Subscribe.objects.create(
                user_id=user_id,
                imp_uid=payment_history.imp_uid,
                expires_at=expires_at,
                is_active=True,
            )
            # 구독 생성 성공 시 is_paid_user 동기화
            user = User.objects.get(id=user_id)
            user.is_paid_user = True
            user.save(update_fields=["is_paid_user"])
            logger.info(
                f"구독 생성 성공: user_id={user_id}, "
                f"imp_uid={payment_history.imp_uid}, "
                f"expires_at={expires_at}"
            )
            return result, subscription

        except Exception as e:
            logger.error(
                f"구독 생성 실패: user_id={user_id}, "
                f"imp_uid={payment_history.imp_uid}, error={e}"
            )
            # 구독 생성 실패 시 결제 이력도 롤백
            payment_history.delete()
            raise ValidationError("구독 생성 중 오류가 발생했습니다.")
