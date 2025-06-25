from typing import cast

from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User

from .models import Subscribe
from .serializers import SubscribeCreateSerializer, SubscribeSerializer
from .services.payment import PaymentService, PaymentVerificationError


class SubscribeListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="내 구독 목록 조회",
        responses={200: SubscribeSerializer(many=True)},
        tags=["구독"],
    )
    def get(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        user = cast(User, request.user)

        subs = Subscribe.objects.filter(user=user)
        serializer = SubscribeSerializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="구독 생성",
        request_body=SubscribeCreateSerializer,
        responses={
            201: SubscribeSerializer(),
            400: "결제 정보 검증 실패",
            409: "이미 구독된 상태거나 유효하지 않은 요청",
            500: "서버 오류",
        },
        tags=["구독"],
    )
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        user = cast(User, request.user)

        serializer = SubscribeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            payment_result, sub = PaymentService().process_subscription_payment(
                user, data["imp_uid"], data["merchant_uid"]
            )
            out = SubscribeSerializer(sub)
            return Response(out.data, status=status.HTTP_201_CREATED)

        except PaymentVerificationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception:
            return Response(
                {"error": "구독 생성 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SubscribeDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request: Request, subscribe_id: int) -> Subscribe:
        if not request.user.is_authenticated:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        user = cast(User, request.user)
        return get_object_or_404(Subscribe, pk=subscribe_id, user=user)

    @swagger_auto_schema(
        operation_summary="구독 상세 조회",
        responses={200: SubscribeSerializer()},
        tags=["구독"],
    )
    def get(self, request: Request, subscribe_id: int) -> Response:
        sub = self.get_object(request, subscribe_id)
        serializer = SubscribeSerializer(sub)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="구독 취소",
        responses={204: "성공적으로 구독이 취소됨", 404: "구독 정보를 찾을 수 없음"},
        tags=["구독"],
    )
    def delete(self, request: Request, subscribe_id: int) -> Response:
        sub = self.get_object(request, subscribe_id)

        sub.is_active = False
        sub.save(update_fields=["is_active"])

        if not request.user.is_authenticated:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        user = cast(User, request.user)

        if not Subscribe.objects.filter(user=user, is_active=True).exists():
            user.is_paid_user = False
            user.save(update_fields=["is_paid_user"])

        return Response(status=status.HTTP_204_NO_CONTENT)
