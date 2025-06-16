import logging
from typing import Any, cast

from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User

from .models import PaymentHistory
from .serializers import PaymentHistorySerializer

logger = logging.getLogger(__name__)


class PaymentHistoryListAPIView(ListAPIView):
    """결제 이력 목록 조회"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self) -> QuerySet[PaymentHistory]:
        """사용자의 결제 이력 목록 조회"""
        user = cast(User, self.request.user)
        return PaymentHistory.objects.filter(user_id=user.id)

    @swagger_auto_schema(
        operation_summary="결제 이력 목록 조회",
        operation_description="현재 로그인한 사용자의 결제 이력 목록을 조회합니다. (삭제된 내역은 제외)",
        responses={
            200: openapi.Response(
                description="결제 이력 목록 조회 성공",
                schema=PaymentHistorySerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user": 3,
                            "user_email": "test@example.com",
                            "imp_uid": "imp_1234567890",
                            "merchant_uid": "order_20240612_0001",
                            "amount": 10000,
                            "status": "paid",
                            "payment_method": "card",
                            "card_name": "신한카드",
                            "card_number": "1234-****-****-5678",
                            "paid_at": "2024-06-12T12:34:56+09:00",
                            "receipt_url": "https://receipt.example.com/imp_1234567890",
                            "created_at": "2024-06-12T12:34:56+09:00",
                            "updated_at": "2024-06-12T12:34:56+09:00",
                            "is_delete": False,
                        }
                    ]
                },
            ),
            401: "인증되지 않은 사용자",
        },
        tags=["결제 이력"],
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """결제 이력 목록 조회"""
        return super().get(request, *args, **kwargs)


class PaymentHistoryDetailAPIView(APIView):
    """결제 이력 상세 조회 및 삭제"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, payment_id: int) -> PaymentHistory:
        """결제 이력 객체 조회"""
        user = cast(User, self.request.user)
        try:
            return PaymentHistory.objects.get(id=payment_id, user_id=user.id)
        except PaymentHistory.DoesNotExist:
            logger.warning(
                f"존재하지 않는 결제 이력 접근 시도: user_id={user.id}, payment_id={payment_id}"
            )
            raise PaymentHistory.DoesNotExist("결제 이력을 찾을 수 없습니다")

    @swagger_auto_schema(
        operation_summary="결제 이력 상세 조회",
        operation_description="특정 결제 이력의 상세 정보를 조회합니다. (삭제된 내역은 제외)",
        responses={
            200: openapi.Response(
                description="결제 이력 상세 조회 성공",
                schema=PaymentHistorySerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 3,
                        "user_email": "test@example.com",
                        "imp_uid": "imp_1234567890",
                        "merchant_uid": "order_20240612_0001",
                        "amount": 10000,
                        "status": "paid",
                        "payment_method": "card",
                        "card_name": "신한카드",
                        "card_number": "1234-****-****-5678",
                        "paid_at": "2024-06-12T12:34:56+09:00",
                        "receipt_url": "https://receipt.example.com/imp_1234567890",
                        "created_at": "2024-06-12T12:34:56+09:00",
                        "updated_at": "2024-06-12T12:34:56+09:00",
                        "is_delete": False,
                    }
                },
            ),
            401: "인증되지 않은 사용자",
            404: "결제 이력을 찾을 수 없음",
            500: openapi.Response(
                description="서버 오류",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="에러 메시지",
                        ),
                    },
                ),
            ),
        },
        tags=["결제 이력"],
    )
    def get(self, request: Request, payment_id: int) -> Response:
        """결제 이력 상세 조회"""
        try:
            payment = self.get_object(payment_id)
            return Response(PaymentHistorySerializer(payment).data)
        except PaymentHistory.DoesNotExist:
            return Response(
                {"error": "결제 이력을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            user = cast(User, request.user)
            logger.error(
                f"결제 이력 상세 조회 실패: user_id={user.id}, payment_id={payment_id}, error={e}"
            )
            return Response(
                {"error": "결제 이력을 조회하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="결제 이력 삭제",
        operation_description="결제 이력을 소프트 딜리트(삭제)합니다. 실제로 DB에서 삭제하지 않고 is_delete만 True로 변경합니다.",
        responses={
            204: "삭제 성공",
            401: "인증되지 않은 사용자",
            404: "결제 이력을 찾을 수 없음",
        },
        tags=["결제 이력"],
    )
    def delete(self, request: Request, payment_id: int) -> Response:
        """결제 이력 소프트 딜리트"""
        try:
            payment = self.get_object(payment_id)
            payment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PaymentHistory.DoesNotExist:
            return Response(
                {"error": "결제 이력을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
