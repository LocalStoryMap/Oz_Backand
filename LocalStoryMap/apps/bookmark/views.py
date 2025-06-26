from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Bookmark, Story
from .serializers import BookmarkSerializer


class BookmarkViewSet(
    mixins.ListModelMixin,  # GET    /bookmarks/
    mixins.DestroyModelMixin,  # DELETE /bookmarks/{id}/
    viewsets.GenericViewSet,
):
    """
    GET    /bookmarks/           → 북마크 목록 조회
    POST   /bookmarks/{id}/      → 스토리 PK로 북마크 추가
    DELETE /bookmarks/{id}/      → 북마크 삭제
    """

    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    # --- list ---
    @swagger_auto_schema(
        tags=["북마크"],
        operation_summary="북마크 목록 조회",
        responses={
            200: openapi.Response(
                description="북마크 목록 반환",
                schema=BookmarkSerializer(many=True),
            )
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # --- add (POST /bookmarks/{id}/) ---
    @action(
        detail=True,
        methods=["post"],
        url_path="",  # ← 빈문자열로 지정해야 /add/ 가 사라집니다
        url_name="add",  # ← operationId/bookmarks_add 로 문서화됩니다
    )
    @swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 추가",
        responses={
            201: openapi.Response(
                description="북마크 추가됨",
                schema=BookmarkSerializer(),
            ),
            200: openapi.Response(
                description="이미 북마크가 존재함",
                schema=BookmarkSerializer(),
            ),
        },
    )
    def add(self, request, pk=None):
        """POST /bookmarks/{pk}/ → story_id=pk"""
        story = get_object_or_404(Story, pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user, story=story
        )
        serializer = self.get_serializer(bookmark)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    # --- destroy (DELETE /bookmarks/{id}/) ---
    @swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 삭제",
        responses={204: openapi.Response(description="북마크 삭제됨", schema=None)},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
