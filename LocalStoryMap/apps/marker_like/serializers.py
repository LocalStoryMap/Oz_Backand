# apps/marker_like/serializers.py
from rest_framework import serializers
from .models import MarkerLike
from apps.marker.models import Marker

class MarkerLikeSerializer(serializers.ModelSerializer):
    # 마커 좋아요 정보 시리얼라이저
    user = serializers.StringRelatedField()
    marker = serializers.StringRelatedField()

    class Meta:
        model = MarkerLike
        fields = ['id', 'user', 'marker', 'is_liked', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'marker', 'created_at', 'updated_at']

class MarkerLikeStatusSerializer(serializers.Serializer):
    # 마커 좋아요 상태 응답 시리얼라이저
    is_liked = serializers.BooleanField()
    like_id = serializers.IntegerField(allow_null=True)
    total_likes = serializers.IntegerField()
