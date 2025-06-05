# apps/users/utils.py
import requests
from django.conf import settings


class KakaoAPI:
    """
    카카오 REST API를 통해 사용자 정보를 가져오는 유틸 클래스.
    """

    @staticmethod
    def get_user_info(access_token: str) -> dict:
        """
        1) 카카오의 /v2/user/me 엔드포인트에 요청을 보내어
        2) JSON 형식으로 유저 정보를 받아옴.

        전달받은 access_token이 유효하지 않으면 예외가 터짐.
        """
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # 예: 토큰 만료, 잘못된 토큰 등
            raise Exception(f"Kakao API 에러: {response.status_code} - {response.text}")

        kakao_json = response.json()

        # kakao_json 예시 구조:
        # {
        #   "id": 1234567890,   # 카카오 고유 user id (int)
        #   "kakao_account": {
        #       "email": "example@kakao.com",     # 이메일 (email 동의 시)
        #       "profile": {
        #           "nickname": "홍길동",
        #           "profile_image_url": "http://.../profile.jpg",
        #           ...
        #       }
        #       ...
        #   }
        #   ...
        # }

        kakao_account = kakao_json.get("kakao_account", {})
        email = kakao_account.get("email", None)
        profile = kakao_account.get("profile", {})

        return {
            "social_id": str(kakao_json.get("id")),  # int → str 변환
            "email": email,
            "nickname": profile.get("nickname"),
            "profile_image": profile.get("profile_image_url"),
        }
