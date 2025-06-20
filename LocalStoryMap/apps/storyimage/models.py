from django.conf import settings
from django.db import models

from apps.story.models import Story
from apps.users.models import User

from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()


class StoryImage(models.Model):
    image_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="storyimages")
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="storyimages"
    )
    image_file = models.ImageField(upload_to="story_images/%Y/%m/%d/", storage=s3_storage,)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "storyimage"
