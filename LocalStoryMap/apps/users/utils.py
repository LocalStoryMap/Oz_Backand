import requests


def get_kakao_user_info(access_token):
    kakao_url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    response = requests.get(kakao_url, headers=headers)
    if response.status_code != 200:
        raise Exception("카카오 사용자 정보 요청 실패")

    return response.json()
