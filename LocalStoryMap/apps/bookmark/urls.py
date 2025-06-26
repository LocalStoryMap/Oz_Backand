from rest_framework.routers import DefaultRouter

from .views import BookmarkViewSet

router = DefaultRouter()
router.register(r"bookmarks", BookmarkViewSet, basename="bookmarks")

urlpatterns = router.urls
