import logging
from urllib.parse import unquote

import requests
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from .utils import KakaoAPI, get_google_user_info


class KakaoLoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="카카오 로그인 (인가 코드 방식)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code"],
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="카카오 인가 코드"
                ),
            },
        ),
        responses={
            200: openapi.Response(description="로그인 성공", schema=UserSerializer),
            400: "실패",
        },
    )
    def post(self, request):
        try:
            code = request.data.get("code")
            if not code:
                return Response({"detail": "authorization code를 전달해주세요."}, status=400)

            # 1) 인가 코드 -> 액세스 토큰 교환
            access_token = KakaoAPI.get_access_token(code)

            # 2) 액세스 토큰으로 사용자 정보 조회
            kakao_user_info = KakaoAPI.get_user_info(access_token)
            social_id = kakao_user_info.get("social_id")
            email = kakao_user_info.get("email")
            nickname = kakao_user_info.get("nickname")
            profile_image = kakao_user_info.get("profile_image")

            if not email:
                return Response(
                    {"detail": "카카오 계정에서 이메일을 확인할 수 없습니다."},
                    status=400,
                )

            # 3) DB에서 기존 유저 조회 or 신규 생성 (이메일 중복 처리 포함)
            try:
                # 이미 kakao로 가입된 유저
                user = User.objects.get(provider="kakao", social_id=social_id)
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                created = False
            except User.DoesNotExist:
                # 다른 provider로 가입된 동일 이메일이 있는지 확인
                existing = User.objects.filter(email=email).first()
                if existing:
                    # 이메일 중복 사용자 -> 로그인만 갱신, 프로필 정보는 유지
                    existing.provider = "kakao"
                    existing.social_id = social_id
                    existing.last_login = timezone.now()
                    set_nick = not existing.nickname and bool(nickname)
                    set_image = not existing.profile_image and bool(profile_image)

                    update_fields = ["provider", "social_id", "last_login"]
                    if set_nick:
                        existing.nickname = nickname
                        update_fields.append("nickname")
                    if set_image:
                        resp = requests.get(profile_image)
                        if resp.status_code == 200:
                            ext = profile_image.split("?")[0].rsplit(".", 1)[-1]
                            fname = f"profile_{existing.id}.{ext}"
                            existing.profile_image.save(
                                fname,
                                ContentFile(resp.content),
                                save=False,
                            )
                        update_fields.append("profile_image")
                    existing.save(update_fields=update_fields)
                    user = existing
                    created = False
                else:
                    # 완전 신규 사용자
                    user = User.objects.create(
                        email=email,
                        nickname=nickname or "",
                        provider="kakao",
                        social_id=social_id,
                    )
                    if profile_image:
                        resp = requests.get(profile_image)
                        if resp.status_code == 200:
                            ext = profile_image.split("?")[0].rsplit(".", 1)[-1]
                            fname = f"profile_{user.id}.{ext}"
                            user.profile_image.save(
                                fname, ContentFile(resp.content), save=True
                            )
                    created = True

            # 4) JWT 토큰 발급
            refresh = RefreshToken.for_user(user)
            access_jwt = str(refresh.access_token)
            refresh_jwt = str(refresh)

            # 5) 응답 구성
            user_data = UserSerializer(user).data
            return Response(
                {
                    "access": access_jwt,
                    "refresh": refresh_jwt,
                    "user": user_data,
                    "is_new_user": created,
                },
                status=200,
            )

        except Exception as e:
            return Response(
                {"detail": f"카카오 로그인 중 오류가 발생했습니다. {str(e)}"},
                status=400,
            )


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Google 소셜 로그인 (인가 코드 방식)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["code"],
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Google OAuth2 인가 코드"
                ),
            },
        ),
        responses={200: openapi.Response(description="JWT 토큰")},
    )
    def post(self, request):
        code = request.data.get("code", "")
        if not code:
            return Response(
                {"error": "code(인가 코드)를 전달해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        code = unquote(code)
        # 1) 구글에서 토큰 교환 & 유저 정보 조회
        try:
            user_info = get_google_user_info(code)
        except Exception as e:
            return Response(
                {"error": "구글 토큰 요청 또는 사용자 정보 조회 실패", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_sub = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture", "")

        # 2) 기존 Google 유저가 있는지 조회
        user = User.objects.filter(provider="google", social_id=google_sub).first()
        if user:
            update_fields = []
            # 2-1) 마지막 로그인 시간은 항상 갱신
            user.last_login = timezone.now()
            update_fields.append("last_login")

            # 2-2) 닉네임이 비어 있을 때만 Google 이름으로 설정
            if not user.nickname and name:
                user.nickname = name
                update_fields.append("nickname")

            # 2-3) 프로필 이미지가 없을 때만 설정
            if picture and not user.profile_image:
                resp = requests.get(picture)
                if resp.status_code == 200:
                    ext = picture.split("?")[0].rsplit(".", 1)[-1]
                    fname = f"profile_{user.id}.{ext}"
                    user.profile_image.save(
                        fname,
                        ContentFile(resp.content),
                        save=False,
                    )
                update_fields.append("profile_image")

            user.save(update_fields=update_fields)
            created = False

        else:
            # 이메일로 가입된 유저가 있는지 확인
            existing = User.objects.filter(email=email).first()
            if existing:
                existing.provider = "google"
                existing.social_id = google_sub
                existing.last_login = timezone.now()

                set_nick = not existing.nickname and bool(name)
                set_image = not existing.profile_image and bool(picture)

                update_fields = ["provider", "social_id", "last_login"]
                if set_nick:
                    existing.nickname = name
                    update_fields.append("nickname")
                if set_image:
                    resp = requests.get(picture)
                    if resp.status_code == 200:
                        ext = picture.split("?")[0].rsplit(".", 1)[-1]
                        fname = f"profile_{existing.id}.{ext}"
                        existing.profile_image.save(
                            fname,
                            ContentFile(resp.content),
                            save=False,
                        )
                    update_fields.append("profile_image")
                existing.save(update_fields=update_fields)

                user = existing
                created = False
            else:
                # 완전 신규 사용자: nickname에 name 저장
                user = User.objects.create(
                    email=email,
                    nickname=name or "",
                    provider="google",
                    social_id=google_sub,
                )
                created = True

                if picture:
                    resp = requests.get(picture)
                    if resp.status_code == 200:
                        ext = picture.split("?")[0].rsplit(".", 1)[-1]
                        fname = f"profile_{user.id}.{ext}"
                        user.profile_image.save(
                            fname, ContentFile(resp.content), save=True
                        )

        # 5) JWT 발급 및 응답
        refresh = RefreshToken.for_user(user)
        access_jwt = str(refresh.access_token)
        refresh_jwt = str(refresh)

        user_data = UserSerializer(user).data
        return Response(
            {
                "access": access_jwt,
                "refresh": refresh_jwt,
                "user": user_data,
                "is_new_user": created,
            },
            status=200,
        )


class LogoutView(APIView):
    """
    1) 클라이언트로부터 Refresh Token을 받아 블랙리스트에 등록 → 로그아웃 처리
    2) 로그인 상태에서만 호출 가능
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="블랙리스트 처리할 Refresh Token"
                ),
            },
        ),
        responses={
            205: openapi.Response(description="로그아웃 성공 (Reset Content)"),
            400: openapi.Response(description="잘못된 요청"),
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh 토큰을 전달해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # RefreshToken 객체 생성 → blacklist() 호출
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(
                {"detail": "토큰 블랙리스트 처리 실패", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 205 Reset Content: 요청을 성공적으로 처리했고, 더 이상 해당 토큰을 사용할 수 없음을 의미
        return Response(status=status.HTTP_205_RESET_CONTENT)


logger = logging.getLogger(__name__)


class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="회원 탈퇴",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="리프레시 토큰 (필수)"
                ),
            },
            required=["refresh"],
        ),
        responses={
            204: openapi.Response(description="회원 탈퇴 성공"),
            400: openapi.Response(description="refresh 토큰을 전달해주세요."),
        },
    )
    def delete(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh 토큰을 전달해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        try:
            with transaction.atomic():
                # 0) 클라이언트가 보낸 refresh 토큰도 블랙리스트
                try:
                    RefreshToken(refresh_token).blacklist()
                except Exception:
                    pass

                # 1) OutstandingToken을 순회하며 개별 예외 무시하고 블랙리스트
                for outstanding in OutstandingToken.objects.filter(user=user):
                    try:
                        RefreshToken(str(outstanding.token)).blacklist()
                    except Exception:
                        # 이미 블랙리스트된 토큰이거나 기타 오류인 경우 무시
                        continue

                # 2) 회원 계정 삭제
                user.delete()

        except Exception as exc:
            logger.error("WithdrawView error", exc_info=exc)
            return Response(
                {"detail": "회원 탈퇴 처리 중 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET    /users/me/   → 내 정보 조회
    PUT    /users/me/   → 내 정보 전체 수정
    PATCH  /users/me/   → 내 정보 일부 수정
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]  # multipart/form-data 지원

    def get_object(self):
        # 인증된 사용자 자신의 레코드만 반환
        return self.request.user

    @swagger_auto_schema(
        operation_summary="내 정보 조회",
        responses={
            200: openapi.Response("내 정보 조회 성공", UserSerializer),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="내 정보 전체 수정 (PUT)",
        request_body=UserSerializer,
        responses={
            200: openapi.Response("내 정보 수정 성공", UserSerializer),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="내 정보 일부 수정 (PATCH)",
        request_body=UserSerializer,
        responses={
            200: openapi.Response("내 정보 부분 수정 성공", UserSerializer),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
