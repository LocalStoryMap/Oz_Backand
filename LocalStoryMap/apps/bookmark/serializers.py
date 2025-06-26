from rest_framework import serializers

from apps.story.serializers import (  # FullStorySerializer import 경로 주의
    FullStorySerializer,
)

from .models import Bookmark, Story


class BookmarkSerializer(serializers.ModelSerializer):
    # create 시에는 story ID만 받고
    story = serializers.PrimaryKeyRelatedField(
        queryset=Story.objects.all(), write_only=True
    )
    # 읽을 때는 스토리 전체 데이터 반환
    story_detail = FullStorySerializer(source="story", read_only=True)

    class Meta:
        model = Bookmark
        fields = ["id", "story", "story_detail"]
        read_only_fields = ["id"]
