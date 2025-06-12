import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscribe
from .serializers import SubscribeInputSerializer, SubscribeSerializer

logger = logging.getLogger(__name__)


class SubscribeListCreateAPIView(APIView):
    # GET  /subscribes/ : 내 구독 조회 (리스트)
    # POST /subscribes/ : 구독 생성 또는 갱신 (입력+결제 검증)

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user_id = request.user.id
        if user_id is None:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        try:
            # 활성 구독만 조회
            subs = Subscribe.objects.filter(user_id=user_id, is_active=True)
            return Response(SubscribeSerializer(subs, many=True).data)
        except Exception as e:
            logger.error(f"구독 목록 조회 실패: user_id={user_id}, error={e}")
            return Response(
                {"error": "구독 목록을 조회하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request: Request) -> Response:
        user_id = request.user.id
        if user_id is None:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")

        try:
            # 시리얼라이저에서 모든 검증 수행
            in_ser = SubscribeInputSerializer(data=request.data)
            in_ser.is_valid(raise_exception=True)

            # 구독 생성/갱신
            defaults = {
                "imp_uid": in_ser.validated_data["imp_uid"],
                "merchant_uid": in_ser.validated_data["merchant_uid"],
                "is_active": True,
                "expires_at": timezone.now()
                + timedelta(days=settings.SINGLE_PLAN_DURATION),
            }
            sub, created = Subscribe.objects.update_or_create(
                user_id=user_id,
                defaults=defaults,
            )
            logger.info(
                f"구독 {'생성' if created else '갱신'} 성공: "
                f"user_id={user_id}, subscribe_id={sub.subscribe_id}"
            )

            return Response(
                SubscribeSerializer(sub).data, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(
                f"구독 생성/갱신 실패: user_id={user_id}, "
                f"imp_uid={request.data.get('imp_uid')}, error={e}"
            )
            # 결제는 성공했지만 구독 생성에 실패한 경우, 환불 처리
            try:
                self._refund_payment(request.data.get("imp_uid"))
            except Exception as refund_error:
                logger.error(f"환불 처리 실패: {refund_error}")
            return Response(
                {"error": "구독 처리 중 오류가 발생했습니다. 결제는 환불되었습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _refund_payment(self, imp_uid: str | None) -> None:
        """결제를 환불합니다."""
        if imp_uid is None:
            logger.error("환불 실패: imp_uid가 None입니다")
            return

        try:
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={"imp_key": settings.IMP_KEY, "imp_secret": settings.IMP_SECRET},
                timeout=5,
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["response"]["access_token"]

            refund_resp = requests.post(
                "https://api.iamport.kr/payments/cancel",
                json={"imp_uid": imp_uid},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5,
            )
            refund_resp.raise_for_status()
            logger.info(f"환불 성공: imp_uid={imp_uid}")

        except requests.exceptions.RequestException as e:
            logger.error(f"환불 실패: imp_uid={imp_uid}, error={e}")
            resp = getattr(e, "response", None)
            code = (
                resp.status_code
                if resp is not None
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            raise Exception(f"환불 처리 중 오류가 발생했습니다: {e}")


class SubscribeDetailAPIView(APIView):
    # GET    /subscribes/{subscribe_id}/ : 특정 구독 조회
    # DELETE /subscribes/{subscribe_id}/ : 구독 취소 (is_active=False 처리)

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, subscribe_id: int) -> Subscribe:
        user_id = self.request.user.id
        if user_id is None:
            raise NotAuthenticated("인증된 사용자만 접근 가능합니다")
        try:
            # 활성 구독만 조회
            return Subscribe.objects.get(
                subscribe_id=subscribe_id,
                user_id=user_id,
                is_active=True,  # 활성 구독만 조회
            )
        except Subscribe.DoesNotExist:
            # 구독이 없거나 비활성화된 경우
            logger.warning(
                f"존재하지 않거나 비활성화된 구독 접근 시도: user_id={user_id}, subscribe_id={subscribe_id}"
            )
            raise Http404("구독을 찾을 수 없습니다")

    def get(self, request: Request, subscribe_id: int) -> Response:
        try:
            sub = self.get_object(subscribe_id)
            return Response(SubscribeSerializer(sub).data)
        except Http404:
            raise
        except Exception as e:
            logger.error(
                f"구독 상세 조회 실패: user_id={request.user.id}, subscribe_id={subscribe_id}, error={e}"
            )
            return Response(
                {"error": "구독 정보를 조회하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request: Request, subscribe_id: int) -> Response:
        try:
            # 활성 구독만 조회 (이미 비활성화된 구독은 404)
            sub = self.get_object(subscribe_id)

            # 구독 상태 업데이트
            try:
                sub.is_active = False
                sub.save(update_fields=["is_active"])
                logger.info(
                    f"구독 취소 완료: user_id={request.user.id}, subscribe_id={subscribe_id}"
                )
            except Exception as e:
                logger.error(
                    f"구독 상태 업데이트 실패: user_id={request.user.id}, subscribe_id={subscribe_id}, error={e}"
                )
                return Response(
                    {"error": "구독 상태 업데이트 중 오류가 발생했습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Http404:
            raise
        except Exception as e:
            logger.error(
                f"구독 취소 중 예상치 못한 오류: user_id={request.user.id}, subscribe_id={subscribe_id}, error={e}"
            )
            return Response(
                {"error": "구독 취소 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
