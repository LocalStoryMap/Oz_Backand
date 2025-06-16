from typing import Any, ClassVar, List, Optional, TypeVar

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

UserType = TypeVar("UserType", bound="User")


class CustomUserManager(UserManager[UserType]):
    """
    수퍼클래스(UserManager)와 완전 동일한 시그니처로 재정의.
    username/email 위치만 바꿔서 email만 쓰도록 내부 로직 처리.
    """

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: Optional[str],
        **extra_fields: Any,
    ) -> UserType:
        if not email:
            raise ValueError("이메일을 반드시 입력해야 합니다.")
        email = self.normalize_email(email)
        user: UserType = self.model(email=email, **extra_fields)  # type: ignore[call-arg]
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> UserType:
        # 시그니처는 (username, email=None, password=None, **)
        actual_email = email or username
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(actual_email, password, **extra_fields)

    def create_superuser(
        self,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> UserType:
        # 시그니처는 수퍼클래스와 동일
        actual_email = email or username
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("슈퍼유저는 is_staff=True, is_superuser=True 이어야 합니다.")

        return self._create_user(actual_email, password, **extra_fields)


class User(AbstractUser):
    """
    · username 필드를 제거하고(email만 인증에 사용)
    · 소셜 로그인 필드를 추가한 커스텀 유저
    """

    # ──────────────────────────────
    # AbstractUser.username(CharField)을 덮어쓰기
    # ──────────────────────────────
    username: ClassVar[None] = None  # type: ignore[assignment,misc]

    # ──────────────────────────────
    # 실제 DB 컬럼으로 사용할 이메일
    # ──────────────────────────────
    email = models.EmailField(
        verbose_name="소셜 계정 이메일",
        max_length=254,
        unique=True,
    )

    # 소셜 로그인 추가 정보
    nickname = models.CharField(max_length=200, blank=True, null=True)
    provider = models.CharField(
        max_length=20,
        choices=(("kakao", "Kakao"), ("google", "Google")),
        default="kakao",
    )
    social_id = models.CharField(max_length=200, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", max_length=300, blank=True, null=True
    )

    is_paid_user = models.BooleanField(default=False)

    # ──────────────────────────────
    # 커스텀 매니저 덮어쓰기
    # ──────────────────────────────
    objects: ClassVar[UserManager["User"]] = CustomUserManager()  # type: ignore[assignment,misc]

    # ──────────────────────────────
    # 인증 관련 설정
    # ──────────────────────────────
    USERNAME_FIELD: ClassVar[str] = "email"  # type: ignore[misc]
    REQUIRED_FIELDS: ClassVar[List[str]] = []

    def __str__(self) -> str:
        return f"{self.email} ({self.provider})"
