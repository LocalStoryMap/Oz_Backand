from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    provider = models.CharField(max_length=30)
    social_id = models.CharField(max_length=100, unique=True)
    profile_image = models.URLField(max_length=500, blank=True, null=True)

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    is_paid_user = models.BooleanField(default=False)  # 인앱결제 유저 여부
    is_staff = models.BooleanField(default=False)  # 관리자 여부

    USERNAME_FIELD = "email"  # 로그인에 사용될 필드 변경
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
