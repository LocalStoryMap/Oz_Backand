from rest_framework import serializers

from apps.users.models import User

from .models import Follow


class FollowUserSerializer(serializers.ModelSerializer):
    """팔로우 대상 사용자 정보 (닉네임, 프로필 이미지 포함)"""

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image"]


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, label="ID")
    follow = FollowUserSerializer(source="followee", read_only=True, label="팔로우 대상 사용자")
    created_at = serializers.DateTimeField(read_only=True, label="생성일")

    class Meta:
        model = Follow
        fields = ["id", "follow", "created_at"]
        read_only_fields = ["id", "created_at"]
