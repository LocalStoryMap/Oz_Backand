from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers, permissions, viewsets
from django.shortcuts import get_object_or_404

from .models import StoryImage
from .serializers import ImageSerializer
from apps.story.models import Story  # Story 모델 import 추가


class StoryImageViewSet(viewsets.ModelViewSet):
    queryset = StoryImage.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_serializer_context(self):
        return {
            "request": self.request,
            "story_id": self.kwargs.get("story_id"),
        }

    def get_queryset(self):
        story_id = self.kwargs.get("story_id")
        if story_id is not None:
            return self.queryset.filter(story__story_id=story_id)
        return self.queryset

    def perform_create(self, serializer):
        story_id = self.kwargs.get("story_id")
        story = get_object_or_404(Story, story_id=story_id)
        serializer.save(user=self.request.user, story=story)

    @swagger_auto_schema(
        tags=["스토리 이미지"],
        operation_summary="스토리 이미지 목록 조회",
        responses={
            200: openapi.Response(
                description="이미지 불러오기 성공.", schema=ImageSerializer(many=True)
            )
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["스토리 이미지"],
        operation_summary="스토리 이미지 생성",
        responses={
            201: openapi.Response(
                description="이미지 생성 성공.", schema=ImageSerializer()
            )
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["스토리 이미지"],
        operation_summary="스토리 이미지 삭제",
        responses={
            204: openapi.Response(description="이미지 삭제 성공.")
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
