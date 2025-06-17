from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets

from .models import Bookmark
from .serializers import BookmarkSerializer


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크",
        responses={
            200: openapi.Response(
                description="북마크 불러오기 성공.", schema=BookmarkSerializer(many=True)
            )
        },
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 추가",
        responses={
            201: openapi.Response(
                description="북마크 추가됨.", schema=BookmarkSerializer(many=True)
            )
        },
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["북마크"],
        operation_summary="스토리 북마크 삭제",
        responses={
            204: openapi.Response(
                description="북마크 삭제됨.", schema=BookmarkSerializer(many=True)
            )
        },
    ),
)
class BookmarkViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Return a list of the current user's bookmarks.

    create:
    Bookmark a story for the current user.

    destroy:
    Remove a bookmark by its ID.
    """

    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
