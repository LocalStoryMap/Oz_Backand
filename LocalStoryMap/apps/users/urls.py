from django.urls import path

from .views import GoogleLoginView, KakaoLoginView, LogoutView

app_name = "users"

urlpatterns = [
    # 카카오 로그인
    path("login/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("login/google/", GoogleLoginView.as_view(), name="google-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
