from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    GoogleLoginView,
    KakaoLoginView,
    LogoutView,
    UserDetailView,
    WithdrawView,
)

app_name = "users"

urlpatterns = [
    # 카카오 로그인
    path("login/kakao/", KakaoLoginView.as_view(), name="kakao-login"),
    path("login/google/", GoogleLoginView.as_view(), name="google-login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
