# serializers.py
from rest_framework import serializers
from .models import StoryImage

class ImageSerializer(serializers.ModelSerializer):
    story_id = serializers.PrimaryKeyRelatedField(
        source='story',
        queryset=StoryImage._meta.get_field('story').related_model.objects.all(),
        write_only=True
    )
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StoryImage
        fields = ['image_id', 'story_id', 'image_file', 'image_url', 'uploaded_at']
        read_only_fields = ['image_id', 'uploaded_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image_file.url)
        return obj.image_file.url  # fallback

    def create(self, validated_data):
        # image_file, story 로직은 ModelViewSet.create에서 자동 처리
        return super().create(validated_data)
