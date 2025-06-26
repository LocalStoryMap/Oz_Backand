# urls.py
from django.urls import path

from .views import BookmarkViewSet

bookmark_list   = BookmarkViewSet.as_view({"get": "list"})
bookmark_detail = BookmarkViewSet.as_view({
    "post":   "add",
    "delete": "destroy",
})

urlpatterns = [
    path("bookmarks/",           bookmark_list,   name="bookmark-list"),
    path("bookmarks/<int:pk>/",  bookmark_detail, name="bookmark-detail"),
]
