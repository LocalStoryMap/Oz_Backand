from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Bookmark, Story
from .serializers import BookmarkSerializer

class BookmarkViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
                      ):
    """
    list:
        북마크 목록 조회 (GET /bookmarks/)

    add:
        스토리 PK로 북마크 추가 (POST /bookmarks/{story_id}/)

    remove:
        스토리 PK로 북마크 삭제 (DELETE /bookmarks/{story_id}/)
    """
    serializer_class    = BookmarkSerializer
    permission_classes  = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 추가",
        responses={
            201: openapi.Response("북마크 추가됨",    schema=BookmarkSerializer()),
            200: openapi.Response("이미 북마크가 존재함", schema=BookmarkSerializer()),
        },
    )
    @action(detail=True, methods=["post"], url_path="", url_name="add")
    def add(self, request, pk=None):
        """POST /bookmarks/{pk}/  → story_id=pk"""
        story, _ = get_object_or_404(Story, pk=pk), None
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            story=story
        )
        serializer = self.get_serializer(bookmark)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 삭제",
        responses={204: openapi.Response("북마크 삭제됨", schema=None)},
    )
    @action(detail=True, methods=["delete"], url_path="", url_name="remove")
    def remove(self, request, pk=None):
        """DELETE /bookmarks/{pk}/  → story_id=pk"""
        bookmark = get_object_or_404(
            Bookmark,
            user=request.user,
            story_id=pk
        )
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
