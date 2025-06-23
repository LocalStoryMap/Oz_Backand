from django.urls import path

from apps.story.apis import (
    CommentDetailAPIView,
    CommentLikeAPIView,
    CommentListAPIView,
    MarkerStoryListAPIView,
    MyStoryListAPIView,
    StoryAPIView,
    StoryDetailAPIView,
    StoryLikeAPIView,
)

app_name = "stories"

urlpatterns = [
    # 스토리 관련 URL
    path("", StoryAPIView.as_view(), name="story-list-create"),
    path("me/", MyStoryListAPIView.as_view(), name="my-story-list"),
    path("<int:story_id>/", StoryDetailAPIView.as_view(), name="story-detail"),
    # 댓글 관련 URL
    path(
        "<int:story_id>/comments/",
        CommentListAPIView.as_view(),
        name="comment-list-create",
    ),
    path(
        "<int:story_id>/comments/<int:comment_id>/",
        CommentDetailAPIView.as_view(),
        name="comment-detail",
    ),
    # 스토리 좋아요 관련 URL
    path("<int:story_id>/likes/", StoryLikeAPIView.as_view(), name="story-like"),
    # 댓글 좋아요 관련 URL
    path(
        "<int:story_id>/comments/<int:comment_id>/likes/",
        CommentLikeAPIView.as_view(),
        name="comment-like",
    ),
    # 마커별 스토리 목록 조회 URL
    path(
        "marker/<int:marker_id>/",
        MarkerStoryListAPIView.as_view(),
        name="marker-story-list",
    ),
]
