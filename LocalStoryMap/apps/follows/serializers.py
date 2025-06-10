from rest_framework import serializers

from .models import Follow


class FollowSerializer(serializers.ModelSerializer):
    id: serializers.IntegerField = serializers.IntegerField(read_only=True, label="ID")
    follow: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        read_only=True, label="팔로우 대상 사용자"
    )
    created_at: serializers.DateTimeField = serializers.DateTimeField(
        read_only=True, label="생성일"
    )

    class Meta:
        model = Follow
        fields = ["id", "follow", "created_at"]
        read_only_fields = ["id", "created_at"]
