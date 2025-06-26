from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationSettingViewSet

router = DefaultRouter()
router.register(r"", NotificationSettingViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
]
