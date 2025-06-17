from rest_framework import serializers

from apps.marker.models import Marker  # 예시용
from apps.users.models import User


class UserSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image"]


class MarkerSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ["id", "title", "description"]
