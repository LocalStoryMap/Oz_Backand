from urllib.parse import unquote

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from .utils import KakaoAPI, get_google_user_info


class KakaoLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="카카오 로그인 (Authorization Code 방식)",
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

            # 3) DB에서 기존 유저 조회 or 신규 생성
            try:
                user = User.objects.get(provider="kakao", social_id=social_id)
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                created = False
            except User.DoesNotExist:
                user = User.objects.create(
                    email=email,
                    nickname=nickname or "",
                    provider="kakao",
                    social_id=social_id,
                    profile_image=profile_image or "",
                    username=email.split("@")[0],
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
    @swagger_auto_schema(
        operation_summary="Google 소셜 로그인 (인가 코드 방식)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Google OAuth2 인가 코드"
                ),
            },
            required=["code"],
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

        # 2) DB 에 이미 provider="google", social_id=google_sub 으로 가입된 유저가 있는지 찾기
        user = User.objects.filter(provider="google", social_id=google_sub).first()
        if user:
            # (A) 완전 처음 로그인은 아님
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])
            created = False
        else:
            # 3) 아직 google social_id 로는 없는 유저 → 이메일 기준으로 있던 유저인지 다시 확인
            user = User.objects.filter(email=email).first()
            if user:
                # (B) 카카오 등으로 이미 가입된 같은 이메일 계정이 있다면, 해당 레코드를 “구글”로 업데이트
                user.provider = "google"
                user.social_id = google_sub
                user.profile_image = picture
                user.last_login = timezone.now()
                user.save(
                    update_fields=[
                        "provider",
                        "social_id",
                        "profile_image",
                        "last_login",
                    ]
                )
                created = False
            else:
                # (C) 완전 신규 이메일
                user = User.objects.create(
                    email=email,
                    username=email.split("@")[0],
                    first_name=name,
                    provider="google",
                    social_id=google_sub,
                    profile_image=picture,
                )
                created = True

        # 4) JWT 발급 및 응답
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "is_new_user": created,
            }
        )
