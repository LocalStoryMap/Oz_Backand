from rest_framework import serializers

from apps.marker.models import Marker
from apps.story.models import Story
from apps.users.models import User


class StorySearchResultSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="story_id", read_only=True)

    class Meta:
        model = Story
        fields = ["id", "title", "content"]


class UserSearchResultSerializer(serializers.ModelSerializer):
    stories = StorySearchResultSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image",
            "stories",
        ]


class MarkerSearchResultSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(source="marker_name", read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Marker
        fields = ["id", "title", "description"]
