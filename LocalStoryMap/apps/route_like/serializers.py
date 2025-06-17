# apps/route_like/serializers.py
from rest_framework import serializers

from apps.route.models import Route

from .models import RouteLike


class RouteLikeSerializer(serializers.ModelSerializer):
    # 경로 좋아요 정보 시리얼라이저
    user: serializers.StringRelatedField = serializers.StringRelatedField()
    route: serializers.StringRelatedField = serializers.StringRelatedField()

    class Meta:
        model = RouteLike
        fields = ["id", "user", "route", "is_liked", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "route", "created_at", "updated_at"]


class RouteLikeStatusSerializer(serializers.Serializer):
    # 경로 좋아요 상태 응답 시리얼라이저
    is_liked = serializers.BooleanField()
    like_id = serializers.IntegerField(allow_null=True)
    total_likes = serializers.IntegerField()
