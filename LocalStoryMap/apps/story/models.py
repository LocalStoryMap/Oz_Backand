from django.db import models

from apps.marker.models import Marker
from apps.users.models import User


class Story(models.Model):
    story_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=100, verbose_name="스토리 제목")
    content = models.TextField(blank=True, verbose_name="스토리 내용")
    emoji = models.CharField(max_length=500, blank=True, verbose_name="스토리 감정 이모티콘")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "story"
        ordering = ["-created_at"]
        verbose_name = "스토리"
        verbose_name_plural = "스토리들"


class StoryComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True
    )
    content = models.TextField(blank=False, verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "story_comment"
        ordering = ["created_at"]


class StoryLike(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_likes")
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "story_like"
        unique_together = [("story", "user")]  # 중복 좋아요 방지
        ordering = ["-created_at"]


class CommentLike(models.Model):
    comment = models.ForeignKey(
        StoryComment, on_delete=models.CASCADE, related_name="likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "story_comment_like"
        unique_together = [("comment", "user")]  # 중복 좋아요 방지
        ordering = ["-created_at"]
