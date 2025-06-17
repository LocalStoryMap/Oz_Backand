from django.conf import settings
from django.db import models

from apps.story.models import Story  # 스토리 모델 있다는 가정


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="bookmarked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "story")
        ordering = ["-created_at"]
