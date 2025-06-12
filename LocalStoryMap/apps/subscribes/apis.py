from datetime import timedelta
from typing import Any, Dict
import logging

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from requests.exceptions import RequestException, Timeout, ConnectionError

from .models import Subscribe
from .serializers import SubscribeInputSerializer, SubscribeSerializer
import requests

from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class IamportAPIError(Exception):
    """아임포트 API 관련 에러"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class SubscribeListCreateAPIView(APIView):

    # GET  /subscribes/ : 내 구독 조회 (리스트)
    # POST /subscribes/ : 구독 생성 또는 갱신 (입력+결제 검증)

    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [AllowAny]  # 테스트용: 누구나 접근 허용

    def _verify_payment(self, imp_uid: str, merchant_uid: str) -> Dict[str, Any]:
        """결제 검증을 수행합니다."""
        try:
            # 1) 토큰 발급
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["response"]["access_token"]

            # 2) 결제 내역 조회
            pay_resp = requests.get(
                f"https://api.iamport.kr/payments/{imp_uid}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5
            )
            pay_resp.raise_for_status()
            payment = pay_resp.json()["response"]

            # 3) 응답 검증
            if payment.get("status") != "paid":
                raise IamportAPIError(
                    f"결제가 완료되지 않았습니다. (상태: {payment.get('status')})",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # 4) 금액 검증
            amount = int(payment.get("amount", 0))
            if amount != settings.SINGLE_PLAN_PRICE:
                raise IamportAPIError(
                    f"결제 금액이 일치하지 않습니다. (기대: {settings.SINGLE_PLAN_PRICE}, 실제: {amount})",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # 5) merchant_uid 검증
            if payment.get("merchant_uid") != merchant_uid:
                raise IamportAPIError(
                    "merchant_uid가 일치하지 않습니다.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            return payment

        except requests.exceptions.Timeout:
            logger.error(f"아임포트 API 타임아웃: imp_uid={imp_uid}")
            raise IamportAPIError(
                "결제 검증 중 시간 초과가 발생했습니다.",
                status_code=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            logger.error(f"아임포트 API 연결 실패: imp_uid={imp_uid}")
            raise IamportAPIError(
                "결제 검증 중 연결 오류가 발생했습니다.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"아임포트 API 호출 실패: imp_uid={imp_uid}, error={str(e)}")
            raise IamportAPIError(
                f"결제 검증 중 오류가 발생했습니다: {str(e)}",
                status_code=e.response.status_code if hasattr(e, 'response') else status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request: Request) -> Response:
        try:
            subs = Subscribe.objects.filter(user=request.user)
            return Response(SubscribeSerializer(subs, many=True).data)
        except Exception as e:
            logger.error(f"구독 목록 조회 실패: user_id={request.user.id}, error={str(e)}")
            return Response(
                {"error": "구독 목록을 조회하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request: Request) -> Response:
        try:
            # 입력 검증
            in_ser = SubscribeInputSerializer(data=request.data)
            in_ser.is_valid(raise_exception=True)

            # 결제 검증
            payment = self._verify_payment(
                in_ser.validated_data["imp_uid"],
                in_ser.validated_data["merchant_uid"]
            )

            # 구독 생성/갱신
            try:
                defaults = {
                    "imp_uid": in_ser.validated_data["imp_uid"],
                    "merchant_uid": in_ser.validated_data["merchant_uid"],
                    "is_active": True,
                    "expires_at": timezone.now() + timedelta(days=settings.SINGLE_PLAN_DURATION),
                }
                sub, created = Subscribe.objects.update_or_create(
                    user=request.user,
                    defaults=defaults,
                )
                logger.info(
                    f"구독 {'생성' if created else '갱신'} 성공: "
                    f"user_id={request.user.id}, subscribe_id={sub.subscribe_id}"
                )

                # 응답
                out_ser = SubscribeSerializer(sub)
                return Response(out_ser.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(
                    f"구독 생성/갱신 실패: user_id={request.user.id}, "
                    f"imp_uid={in_ser.validated_data['imp_uid']}, error={str(e)}"
                )
                # 결제는 성공했지만 구독 생성에 실패한 경우, 환불 처리
                try:
                    self._refund_payment(in_ser.validated_data["imp_uid"])
                except Exception as refund_error:
                    logger.error(f"환불 처리 실패: {str(refund_error)}")
                
                return Response(
                    {"error": "구독 처리 중 오류가 발생했습니다. 결제는 환불되었습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except IamportAPIError as e:
            logger.error(f"결제 검증 실패: {str(e)}")
            return Response(
                {"error": str(e)},
                status=e.status_code or status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"구독 생성 중 예상치 못한 오류: {str(e)}")
            return Response(
                {"error": "구독 처리 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _refund_payment(self, imp_uid: str) -> None:
        """결제를 환불합니다."""
        try:
            # 토큰 발급
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["response"]["access_token"]

            # 환불 요청
            refund_resp = requests.post(
                "https://api.iamport.kr/payments/cancel",
                json={"imp_uid": imp_uid},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5
            )
            refund_resp.raise_for_status()
            logger.info(f"환불 성공: imp_uid={imp_uid}")

        except requests.exceptions.RequestException as e:
            logger.error(f"환불 실패: imp_uid={imp_uid}, error={str(e)}")
            raise IamportAPIError(
                f"환불 처리 중 오류가 발생했습니다: {str(e)}",
                status_code=e.response.status_code if hasattr(e, 'response') else status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubscribeDetailAPIView(APIView):

    # GET    /subscribes/{subscribe_id}/ : 특정 구독 조회
    # DELETE /subscribes/{subscribe_id}/ : 구독 취소 (is_active=False 처리)

    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [AllowAny]  # 테스트용: 누구나 접근 허용

    def get_object(self, subscribe_id: int) -> Subscribe:
        try:
            return Subscribe.objects.get(
                subscribe_id=subscribe_id,
                user=self.request.user,
            )
        except Subscribe.DoesNotExist:
            logger.warning(
                f"존재하지 않는 구독 접근 시도: "
                f"user_id={self.request.user.id}, subscribe_id={subscribe_id}"
            )
            raise Http404("구독을 찾을 수 없습니다")

    def get(self, request: Request, subscribe_id: int) -> Response:
        try:
            sub = self.get_object(subscribe_id)
            return Response(SubscribeSerializer(sub).data)
        except Http404 as e:
            raise
        except Exception as e:
            logger.error(
                f"구독 상세 조회 실패: "
                f"user_id={request.user.id}, subscribe_id={subscribe_id}, error={str(e)}"
            )
            return Response(
                {"error": "구독 정보를 조회하는 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _cancel_payment(self, imp_uid: str, merchant_uid: str) -> None:
        """결제를 취소합니다."""
        try:
            # 토큰 발급
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["response"]["access_token"]

            # 결제 취소
            cancel_resp = requests.post(
                "https://api.iamport.kr/payments/cancel",
                json={"imp_uid": imp_uid, "merchant_uid": merchant_uid},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5
            )
            cancel_resp.raise_for_status()
            logger.info(f"결제 취소 성공: imp_uid={imp_uid}")

        except requests.exceptions.RequestException as e:
            logger.error(f"결제 취소 실패: imp_uid={imp_uid}, error={str(e)}")
            raise IamportAPIError(
                f"결제 취소 중 오류가 발생했습니다: {str(e)}",
                status_code=e.response.status_code if hasattr(e, 'response') else status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _unschedule_payment(self, customer_uid: str) -> None:
        """정기결제 예약을 해제합니다."""
        try:
            # 토큰 발급
            token_resp = requests.post(
                "https://api.iamport.kr/users/getToken",
                json={
                    "imp_key": settings.IMP_KEY,
                    "imp_secret": settings.IMP_SECRET,
                },
                timeout=5
            )
            token_resp.raise_for_status()
            access_token = token_resp.json()["response"]["access_token"]

            # 정기결제 예약 해제
            unschedule_resp = requests.post(
                "https://api.iamport.kr/subscribe/payments/unschedule",
                json={"customer_uid": customer_uid},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5
            )
            unschedule_resp.raise_for_status()
            logger.info(f"정기결제 예약 해제 성공: customer_uid={customer_uid}")

        except requests.exceptions.RequestException as e:
            logger.error(f"정기결제 예약 해제 실패: customer_uid={customer_uid}, error={str(e)}")
            raise IamportAPIError(
                f"정기결제 예약 해제 중 오류가 발생했습니다: {str(e)}",
                status_code=e.response.status_code if hasattr(e, 'response') else status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request: Request, subscribe_id: int) -> Response:
        try:
            sub = self.get_object(subscribe_id)

            # 1) 결제 취소
            try:
                self._cancel_payment(sub.imp_uid, sub.merchant_uid)
            except IamportAPIError as e:
                logger.error(f"결제 취소 실패: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=e.status_code or status.HTTP_400_BAD_REQUEST
                )

            # 2) 정기결제 예약 해제
            if hasattr(sub, "customer_uid"):
                try:
                    self._unschedule_payment(sub.customer_uid)
                except IamportAPIError as e:
                    logger.error(f"정기결제 예약 해제 실패: {str(e)}")
                    # 정기결제 예약 해제 실패는 치명적이지 않으므로 계속 진행

            # 3) 구독 상태 업데이트
            try:
                sub.is_active = False
                sub.save(update_fields=["is_active"])
                logger.info(
                    f"구독 취소 완료: user_id={request.user.id}, "
                    f"subscribe_id={subscribe_id}"
                )
            except Exception as e:
                logger.error(
                    f"구독 상태 업데이트 실패: user_id={request.user.id}, "
                    f"subscribe_id={subscribe_id}, error={str(e)}"
                )
                return Response(
                    {"error": "구독 상태 업데이트 중 오류가 발생했습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Http404 as e:
            raise
        except Exception as e:
            logger.error(
                f"구독 취소 중 예상치 못한 오류: "
                f"user_id={request.user.id}, subscribe_id={subscribe_id}, error={str(e)}"
            )
            return Response(
                {"error": "구독 취소 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
