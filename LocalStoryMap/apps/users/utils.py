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
            "client_secret": settings.KAKAO_CLIENT_SECRET,
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


def get_google_user_info(code: str) -> dict:
    """
    1) 인가 코드를 토큰으로 교환
    2) 토큰으로 사용자 정보 조회
    """
    # 1) 액세스 토큰 요청
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
    }
    token_resp = requests.post(token_url, data=data)
    token_resp.raise_for_status()
    access_token = token_resp.json().get("access_token")

    # 2) 사용자 정보 조회 (OpenID Connect)
    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_resp = requests.get(userinfo_url, headers=headers)
    userinfo_resp.raise_for_status()
    return userinfo_resp.json()
