from django.conf import settings
from django.db import models


class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Story #{self.id} - {self.title}"


class StoryImage(models.Model):
    image_id = models.BigAutoField(primary_key=True)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="storyimages"
    )
    image_file = models.ImageField(upload_to="story_images/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "storyimage"