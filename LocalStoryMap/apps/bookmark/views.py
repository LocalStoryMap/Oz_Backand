from rest_framework import mixins, viewsets, permissions
from .models import Bookmark
from .serializers import BookmarkSerializer

class BookmarkViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
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
