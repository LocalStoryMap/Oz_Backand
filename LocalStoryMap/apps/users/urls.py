from django.urls import path

from .views import GoogleLoginView, KakaoLoginView

app_name = "users"

urlpatterns = [
    # 카카오 로그인
    path("login/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("login/google/", GoogleLoginView.as_view(), name="google-login"),
]
