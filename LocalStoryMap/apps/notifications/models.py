from django.conf import settings
from django.db import models


class Notification(models.Model):
    FOLLOW = "follow"
    LIKE = "like"
    COMMENT_REPLY = "comment_reply"
    TYPE_CHOICES = [
        (FOLLOW, "Follow"),
        (LIKE, "Like"),
        (COMMENT_REPLY, "Comment Reply"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_notifications",
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class NotificationSetting(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        (Notification.FOLLOW, "Follow"),
        (Notification.LIKE, "Like"),
        (Notification.COMMENT_REPLY, "Comment Reply"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "type")
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.user} - {self.type}"
