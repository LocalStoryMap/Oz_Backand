from django.conf import settings
from django.db import models

from apps.story.models import Story


class StoryImage(models.Model):
    image_id = models.BigAutoField(primary_key=True)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="storyimages"
    )
    image_file = models.ImageField(upload_to="story_images/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "storyimage"
