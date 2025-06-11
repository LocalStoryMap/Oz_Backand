from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import StoryImageViewSet

# 기본 이미지 CRUD
router = DefaultRouter()
# router.register(r'stories', StoryViewSet, basename='story')
router.register(r'images', StoryImageViewSet, basename='image')
# → /api/images/, /api/images/{pk}/

# stories/{pk}/images
# nested = routers.NestedDefaultRouter(router, r'stories', lookup='story')
# nested.register(r'images', StoryImageViewSet, basename='story-images')
# → /api/stories/{story_pk}/images/, /api/stories/{story_pk}/images/{pk}/

urlpatterns = [
    path("", include(router.urls)),    # /images, /images/{pk}
    # path("", include(nested.urls)),    # /stories/{pk}/images, /stories/{pk}/images/{pk}
]
