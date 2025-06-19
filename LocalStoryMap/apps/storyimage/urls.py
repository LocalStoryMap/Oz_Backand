from django.urls import path

from .views import StoryImageViewSet

story_image_list = StoryImageViewSet.as_view({"get": "list", "post": "create"})
story_image_detail = StoryImageViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    path("stories/<str:story_id>/images/", story_image_list, name="story-image-list"),
    path(
        "stories/<str:story_id>/images/<int:pk>/",
        story_image_detail,
        name="story-image-detail",
    ),
]
