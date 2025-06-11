from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    AbstractUser를 상속받아 기본 필드(username, password 등)를 유지하면서,
    소셜 로그인 관련 필드와 추가 정보를 정의함.
    """

    # 1) 이메일을 소셜 계정 식별자로 사용하기 위해, unique=True로 설정(카카오/구글 이메일 중복 방지)
    email = models.EmailField(
        verbose_name="소셜 계정 이메일",
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )

    # 2) 사용자의 닉네임 (소셜 프로플에 있으면 가져오고, 없으면 빈 문자열 처리)
    nickname = models.CharField(
        verbose_name="사용자 닉네임",
        max_length=50,
        blank=True,
        null=True,
    )

    # 3) 소셜 제공자 구분 (ex. kakao , google)
    provider = models.CharField(
        verbose_name="소셜 제공자",
        max_length=20,
        choices=(("kakao", "Kakao"), ("google", "Google")),
        default="kakao",
    )

    # 4) 소셜 플랫폼에서 발급해 주는 고유 ID (string으로 저장)
    social_id = models.CharField(
        verbose_name="소셜 고유 ID",
        max_length=100,
        blank=True,
        null=True,
        help_text="카카오 또는 구글에서 제공하는 유저 고유 ID",
    )

    # 5) 프로필 이미지
    profile_image = models.ImageField(
        verbose_name="프로필 이미지",
        upload_to="profile_images/",
        blank=True,
        null=True,
    )

    # 6) 인앱 결제 여부 -> default=False
    is_paid_user = models.BooleanField(
        verbose_name="인앱 결제 여부",
        default=False,
    )

    # AbstractUser에 이미 email, username, password, is_staff, is_active, date_joined, last_login 등이 포함됨
    # 따라서, is_active는 AbstractUser에서 default=True로 이미 관리됨.

    # ------------------------------------------------------------------------------
    # **id**(AutoField PK), **first_name**, **last_name** 등은 AbstractUser가 제공 → 그대로 사용
    # ------------------------------------------------------------------------------
    # ※ USERNAME_FIELD를 'email'로 변경하여, 로그인 시 이메일을 식별자로 사용하도록 할 수 있음
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email을 USERNAME_FIELD로 쓰기 떄문에, 필수필드 목록을 비워둠

    def __str__(self):
        return f"{self.email}({self.provider})"
