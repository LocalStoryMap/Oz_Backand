from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import User

from .models import Follow


class FollowCreateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=300, help_text="팔로우할 사용자의 닉네임")

    def validate_nickname(self, nickname):
        try:
            return User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            raise serializers.ValidationError("해당 닉네임의 사용자가 없습니다.")

    def create(self, validated_data):
        request = self.context["request"]

        # ─── 테스트용: 로그인 안 된 경우 DEBUG=True 일 때만 ID=4 유저로 팔로워 설정 ───
        if not request.user or not request.user.is_authenticated:
            follower = get_user_model().objects.get(pk=4)
        else:
            follower = request.user
        # ─────────────────────────────────────────────────────────────────────────────

        followee = validated_data["nickname"]
        if follower == followee:
            raise serializers.ValidationError("스스로를 팔로우할 수 없습니다.")
        follow, created = Follow.objects.get_or_create(
            follower=follower,
            followee=followee,
        )
        if not created:
            raise serializers.ValidationError("이미 팔로우 중입니다.")
        return follow


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image"]


class FollowSerializer(serializers.ModelSerializer):
    follow = FollowUserSerializer(source="followee", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follow", "created_at"]
        read_only_fields = ["id", "created_at"]
