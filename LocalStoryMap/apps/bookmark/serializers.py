from rest_framework import serializers

from .models import Bookmark, Story


class BookmarkSerializer(serializers.ModelSerializer):
    # create 시엔 write_only로 story_id만 받고, response 땐 포함 안 함
    story = serializers.PrimaryKeyRelatedField(
        queryset=Story.objects.all(), write_only=True
    )
    # 읽기 전용으로 response에만 포함
    marker_name = serializers.CharField(
        source="story.marker.marker_name", read_only=True
    )

    adress = serializers.CharField(source="story.marker.adress", read_only=True)

    class Meta:
        model = Bookmark
        fields = ["story", "marker_name", "adress"]
