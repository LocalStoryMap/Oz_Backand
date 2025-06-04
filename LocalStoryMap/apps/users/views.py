import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User

class KakaoLoginView(APIView):

    @swagger_auto_schema(
        operation_summary="카카오 로그인",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='카카오 인가 코드'),
            },
        ),
        responses={200: "로그인 성공(JWT 토큰 발급)", 400: "실패"}
    )
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "인가 코드가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 인가 코드 → access token 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }
        token_headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        token_res = requests.post(token_url, data=token_data, headers=token_headers)

        if token_res.status_code != 200:
            return Response({"error": "카카오 access_token 요청 실패"}, status=token_res.status_code)

        access_token = token_res.json().get("access_token")

        # 2. access token으로 사용자 정보 요청
        profile_url = "https://kapi.kakao.com/v2/user/me"
        profile_headers = {"Authorization": f"Bearer {access_token}"}
        profile_res = requests.get(profile_url, headers=profile_headers)

        if profile_res.status_code != 200:
            return Response({"error": "카카오 사용자 정보 요청 실패"}, status=profile_res.status_code)

        kakao_data = profile_res.json()
        kakao_id = kakao_data.get("id")
        kakao_account = kakao_data.get("kakao_account", {})
        email = kakao_account.get("email")
        nickname = kakao_account.get("profile", {}).get("nickname")
        profile_image = kakao_account.get("profile", {}).get("profile_image_url")

        if not email or not kakao_id:
            return Response({"error": "카카오 계정에 이메일이 없습니다."}, status=400)

        # 3. 사용자 등록 or 조회
        user, created = User.objects.get_or_create(
            social_id=str(kakao_id),
            provider="kakao",
            defaults={
                "email": email,
                "username": nickname or f"카카오유저_{kakao_id}",
                "profile_image": profile_image,
                "is_active": True,
            }
        )

        # 4. JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "provider": user.provider,
                "profile_image": user.profile_image,
            }
        })

