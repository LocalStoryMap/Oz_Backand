from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    커스텀 User 모델을 Admin에 등록
    """

    # 관리자 화면 목록에 표시할 컬럼
    list_display = (
        "email",
        "provider",
        "social_id",
        "is_paid_user",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "provider",
        "is_paid_user",
        "is_staff",
        "is_active",
        "groups",
    )
    search_fields = ("email", "social_id", "nickname")
    ordering = ("email",)

    # 상세(edit) 페이지 필드셋
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("nickname", "profile_image")}),
        (_("Social info"), {"fields": ("provider", "social_id", "is_paid_user")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # 슈퍼유저 생성(create) 페이지 필드셋
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
