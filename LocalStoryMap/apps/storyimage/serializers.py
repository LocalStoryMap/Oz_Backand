from rest_framework import serializers

from apps.story.models import Story

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
        request = self.context.get("request")
        print("🔥 user:", request.user)  # 로그 확인
        validated_data["user"] = request.user
        return super().create(validated_data)
