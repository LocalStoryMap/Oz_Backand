from enum import Enum
from typing import Any, Self, TypeVar

from django.db import models

T = TypeVar("T", bound="PaymentHistory")


class PaymentStatus(str, Enum):
    """결제 상태"""

    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentHistoryManager(models.Manager[T]):
    """결제 이력 매니저"""

    def get_queryset(self) -> models.QuerySet[T]:
        """기본 쿼리셋 (삭제되지 않은 결제 이력만)"""
        return super().get_queryset().filter(is_delete=False)


class PaymentHistory(models.Model):
    """결제 이력"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payment_histories",
    )
    imp_uid = models.CharField(max_length=255, unique=True)
    merchant_uid = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.value) for status in PaymentStatus],
    )
    payment_method = models.CharField(max_length=50, null=True)
    card_name = models.CharField(max_length=100, null=True)
    card_number = models.CharField(max_length=50, null=True)
    paid_at = models.DateTimeField(null=True)
    receipt_url = models.URLField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False, verbose_name="삭제 여부")

    # 매니저 정의
    objects: PaymentHistoryManager[Self] = PaymentHistoryManager()
    all_objects: models.Manager[Self] = models.Manager()

    class Meta:
        db_table = "payment_histories"
        ordering = ["-created_at"]
        verbose_name = "결제 이력"
        verbose_name_plural = "결제 이력 목록"

    def __str__(self) -> str:
        return f"{self.user.email} - {self.imp_uid} ({self.amount}원)"

    def delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        """결제 이력 삭제 (소프트 삭제)

        실제로 DB에서 삭제하지 않고, is_delete 필드만 True로 설정합니다.
        """
        self.is_delete = True
        self.save(update_fields=["is_delete", "updated_at"])
        return (1, {"paymenthistory.PaymentHistory": 1})
