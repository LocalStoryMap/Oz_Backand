# storyimage/views.py
from rest_framework import parsers, permissions, viewsets

from .models import StoryImage
from .serializers import ImageSerializer


class StoryImageViewSet(viewsets.ModelViewSet):
    queryset = StoryImage.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        # 1) nested router가 전달하는 story_pk가 있으면 해당 스토리 이미지만 리턴
        story_pk = self.kwargs.get("story_pk")
        if story_pk is not None:
            return self.queryset.filter(story_id=story_pk)

        # 2) 그렇지 않으면 전체 Image 리스트
        return self.queryset
