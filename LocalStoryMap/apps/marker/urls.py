# apps/marker/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MarkerViewSet

router = DefaultRouter()
router.register(r"markers", MarkerViewSet, basename="marker")

urlpatterns = [
    path("", include(router.urls)),
]
