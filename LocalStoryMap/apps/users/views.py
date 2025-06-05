# apps/users/views.py
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from .utils import KakaoAPI


class KakaoLoginView(APIView):
    """
    POST /users/login/kakao/
    1) request.data에 있는 'access_token'으로 카카오 API에서 유저 정보 조회
    2) 이메일(email), social_id 등을 기준으로 기존 유저가 있는지 확인
    3) 없으면 새로 생성, 있으면 해당 유저 가져오기
    4) simplejwt로 JWT 토큰(access, refresh) 발급
    5) 응답(JSON)으로 { access, refresh, user: { … } } 반환
    """

    permission_classes = [permissions.AllowAny]  # 인증 필요 없이 접근 허용

    @swagger_auto_schema(
        operation_summary="카카오 소셜 로그인",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["access_token"],
            properties={
                "access_token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="카카오에서 받아온 access token"
                ),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access": openapi.Schema(
                        type=openapi.TYPE_STRING, description="발급된 JWT Access Token"
                    ),
                    "refresh": openapi.Schema(
                        type=openapi.TYPE_STRING, description="발급된 JWT Refresh Token"
                    ),
                    "user": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "email": openapi.Schema(type=openapi.TYPE_STRING),
                            "nickname": openapi.Schema(type=openapi.TYPE_STRING),
                            "provider": openapi.Schema(type=openapi.TYPE_STRING),
                            "social_id": openapi.Schema(type=openapi.TYPE_STRING),
                            "profile_image": openapi.Schema(type=openapi.TYPE_STRING),
                            "is_paid_user": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "date_joined": openapi.Schema(
                                type=openapi.TYPE_STRING, format="date-time"
                            ),
                            "last_login": openapi.Schema(
                                type=openapi.TYPE_STRING, format="date-time"
                            ),
                        },
                    ),
                    "is_new_user": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                },
            ),
            400: "Bad Request (access_token 누락 또는 토큰 불일치 등)",
        },
    )
    def post(self, request):
        try:
            # 1) 클라이언트가 보낸 access_token
            kakao_access_token = request.data.get("access_token")
            if not kakao_access_token:
                return Response(
                    {"detail": "access_token을 전달해주세요."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2) 카카오 API로부터 유저 정보 가져오기
            kakao_user_info = KakaoAPI.get_user_info(kakao_access_token)
            social_id = kakao_user_info.get("social_id")
            email = kakao_user_info.get("email")
            nickname = kakao_user_info.get("nickname")
            profile_image = kakao_user_info.get("profile_image")

            # 이메일이 없을 경우 (카카오 계정 설정에 따라 email 동의를 하지 않은 경우) → 에러 처리
            if not email:
                return Response(
                    {"detail": "카카오 계정에서 이메일을 확인할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3) DB(User 테이블)에서 이미 가입된 사용자인지 확인
            #      - provider='kakao', social_id=... 로 유니크하게 찾기
            try:
                user = User.objects.get(provider="kakao", social_id=social_id)
                # 기존 유저 → last_login timestamp 업데이트
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                created = False
            except User.DoesNotExist:
                # 4) 새로운 유저 생성
                user = User.objects.create(
                    email=email,
                    nickname=nickname or "",  # nickname이 없으면 빈 문자열
                    provider="kakao",
                    social_id=social_id,
                    profile_image=profile_image or "",
                    # username, password 등은 AbstractUser 요구사항이지만,
                    # USERNAME_FIELD를 email로 지정했으므로 username은 빈 문자열로 처리
                    username=email.split("@")[0],  # 예시로 email 앞부분을 username에 넣어둠
                )
                created = True

            # 5) JWT 토큰 발급 (RefreshToken ⇒ access token, refresh token 모두 발급)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # 6) 유저 객체 직렬화 (시리얼라이저 사용)
            user_data = UserSerializer(user).data

            # 7) 응답 보내기
            return Response(
                {
                    "access": access_token,
                    "refresh": refresh_token,
                    "user": user_data,
                    "is_new_user": created,  # 필요하다면 가입 여부를 알려줄 수도 있음
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # 카카오 API 호출 실패, DB 오류 등 모든 예외를 잡아서 400 Bad Request 리턴
            return Response(
                {"detail": f"카카오 로그인 중 오류가 발생했습니다. {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
