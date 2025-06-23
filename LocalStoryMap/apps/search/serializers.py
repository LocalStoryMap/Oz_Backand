from rest_framework import serializers

from apps.marker.models import Marker  # 예시용
from apps.story.models import Story
from apps.users.models import User


class StorySearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "title", "content"]


class UserSearchResultSerializer(serializers.ModelSerializer):
    stories = StorySearchResultSerializer(many=True, source="stories")

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image",
            "stories",
        ]


class MarkerSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ["id", "title", "description"]
