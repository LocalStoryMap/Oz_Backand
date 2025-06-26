# apps/services/payment.py

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

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
        def parse_datetime(val):
            if val is None:
                return None
            if isinstance(val, str):
                try:
                    return datetime.fromisoformat(val)
                except:
                    return None
            try:
                return datetime.fromtimestamp(int(val))
            except:
                return None

        return cls(
            imp_uid=payment["imp_uid"],
            merchant_uid=payment["merchant_uid"],
            amount=int(payment["amount"]),
            payment_method=payment.get("pay_method"),
            card_name=payment.get("card_name"),
            card_number=payment.get("card_number"),
            paid_at=parse_datetime(payment.get("paid_at")),
            receipt_url=payment.get("receipt_url"),
            raw_data=payment,
        )


class PaymentVerificationError(Exception):
    pass


class ImpClient:
    def __init__(self) -> None:
        self.base_url = "https://api.iamport.kr"
        self._access_token: Optional[str] = None

    def _get_token(self) -> str:
        if self._access_token:
            return self._access_token
        try:
            resp = requests.post(
                f"{self.base_url}/users/getToken",
                json={"imp_key": settings.IMP_KEY, "imp_secret": settings.IMP_SECRET},
                timeout=5,
            )
            resp.raise_for_status()
            token = resp.json()["response"]["access_token"]
            if not token:
                raise PaymentVerificationError("토큰 발급 실패")
            self._access_token = token
            return token
        except requests.RequestException as e:
            logger.error(f"토큰 발급 실패: {e}")
            raise PaymentVerificationError("결제 검증 중 오류가 발생했습니다.")

    def get_payment(self, imp_uid: str) -> Dict[str, Any]:
        try:
            resp = requests.get(
                f"{self.base_url}/payments/{imp_uid}",
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=5,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except requests.RequestException as e:
            logger.error(f"결제 내역 조회 실패: {e}")
            raise PaymentVerificationError("결제 내역을 조회하는 중 오류가 발생했습니다.")


class PaymentService:
    def __init__(self, imp_client: Optional[ImpClient] = None) -> None:
        self.imp_client = imp_client or ImpClient()

    def process_subscription_payment(
        self, user: User, imp_uid: str, merchant_uid: str
    ) -> Tuple[PaymentResult, Subscribe]:
        user_id = user.id

        # 1️⃣ 멱등성 처리
        existing = Subscribe.objects.filter(
            user_id=user_id, merchant_uid=merchant_uid, is_active=True
        ).first()
        if existing:
            # 기존 구독과 페이먼트 결과를 stub으로 반환
            stub = PaymentResult(
                imp_uid, merchant_uid, 0, None, None, None, None, None, {}
            )
            return stub, existing

        # 2️⃣ 포트원 API 호출 & 검증
        payment = self.imp_client.get_payment(imp_uid)
        if payment.get("status") != "paid":
            raise PaymentVerificationError("결제가 완료되지 않았습니다.")
        if payment.get("merchant_uid") != merchant_uid:
            raise PaymentVerificationError("merchant_uid가 일치하지 않습니다.")
        amount = int(payment.get("amount", 0))
        if amount != settings.SINGLE_PLAN_PRICE:
            raise PaymentVerificationError(
                f"결제 금액 불일치: 기대={settings.SINGLE_PLAN_PRICE}, 실제={amount}"
            )

        # 3️⃣ 결과 파싱
        result = PaymentResult.from_payment(payment)

        # 4️⃣ 트랜잭션 단위로 이력 + 구독 생성
        with transaction.atomic():
            # 4-1) 결제 이력 저장
            history = PaymentHistory.objects.create(
                user=user,
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

            # 4-2) 구독 생성 (merchant_uid 필수 저장)
            expires_at = timezone.now() + timedelta(days=settings.SINGLE_PLAN_DURATION)
            subscription = Subscribe.objects.create(
                user=user,
                imp_uid=history.imp_uid,
                merchant_uid=history.merchant_uid,
                expires_at=expires_at,
                is_active=True,
            )

            # 4-3) 사용자 상태 동기화
            user.is_paid_user = True
            user.save(update_fields=["is_paid_user"])

        return result, subscription
