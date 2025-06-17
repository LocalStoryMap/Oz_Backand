from django.urls import path

from apps.story.apis import (
    CommentDetailAPIView,
    CommentLikeDetailAPIView,
    CommentLikeListAPIView,
    CommentListAPIView,
    StoryAPIView,
    StoryDetailAPIView,
    StoryLikeDetailAPIView,
    StoryLikeListAPIView,
)

app_name = "stories"

urlpatterns = [
    # 스토리 관련 URL
    path("", StoryAPIView.as_view(), name="story-list-create"),
    path("<int:story_id>/", StoryDetailAPIView.as_view(), name="story-detail"),
    # 댓글 관련 URL
    path(
        "<int:story_id>/comments/",
        CommentListAPIView.as_view(),
        name="comment-list-create",
    ),
    path(
        "comments/<int:comment_id>/",
        CommentDetailAPIView.as_view(),
        name="comment-detail",
    ),
    # 스토리 좋아요 관련 URL
    path(
        "<int:story_id>/likes/", StoryLikeListAPIView.as_view(), name="story-like-list"
    ),
    path(
        "<int:story_id>/likes/<int:user_id>/",
        StoryLikeDetailAPIView.as_view(),
        name="story-like-detail",
    ),
    # 댓글 좋아요 관련 URL
    path(
        "comments/<int:comment_id>/likes/",
        CommentLikeListAPIView.as_view(),
        name="comment-like-list",
    ),
    path(
        "comments/<int:comment_id>/likes/<int:user_id>/",
        CommentLikeDetailAPIView.as_view(),
        name="comment-like-detail",
    ),
]
