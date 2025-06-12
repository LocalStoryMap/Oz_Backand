from rest_framework import serializers

# Story 모델을 명시적으로 import 합니다.
from apps.storyimage.models import Story

from .models import StoryImage


class ImageSerializer(serializers.ModelSerializer):
    # story_id 필드에 타입 애너테이션을 추가하고, 직접 import한 Story 모델을 사용
    story_id: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        source="story",
        queryset=Story.objects.all(),
        write_only=True,
    )
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StoryImage
        fields = ["image_id", "story_id", "image_file", "image_url", "uploaded_at"]
        read_only_fields = ["image_id", "uploaded_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image_file.url)
        return obj.image_file.url  # fallback

    def create(self, validated_data):
        # image_file과 story 관계는 ModelViewSet.create에서 자동 처리됩니다.
        return super().create(validated_data)
