from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    로그인 성공 후 또는 마이페이지 조회 시,
    유저 정보를 JSON 형태로 변환해 주는 시리얼라이저
    """

    class Meta:
        model = User
        # 클라이언트에 노출하고자 하는 필드를 적음
        fields = [
            "id",
            "email",
            "nickname",
            "provider",
            "social_id",
            "profile_image",
            "is_paid_user",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "email",
            "provider",
            "social_id",
            "date_joined",
            "last_login",
        ]
