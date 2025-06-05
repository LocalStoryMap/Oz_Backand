import requests
from django.conf import settings


class KakaoAPI:
    @staticmethod
    def get_access_token(code: str) -> str:
        """
        카카오 인가 코드(authorization code)를 통해 액세스 토큰을 발급받습니다.
        """
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        response = requests.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"토큰 교환 실패: {response.status_code} - {response.text}")

        return response.json().get("access_token")

    @staticmethod
    def get_user_info(access_token: str) -> dict:
        """
        이미 발급받은 액세스 토큰으로 사용자 정보를 조회합니다.
        """
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Kakao API 에러: {response.status_code} - {response.text}")

        kakao_json = response.json()
        kakao_account = kakao_json.get("kakao_account", {})
        email = kakao_account.get("email", None)
        profile = kakao_account.get("profile", {})

        return {
            "social_id": str(kakao_json.get("id")),
            "email": email,
            "nickname": profile.get("nickname"),
            "profile_image": profile.get("profile_image_url"),
        }
