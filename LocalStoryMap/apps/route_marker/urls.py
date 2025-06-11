# apps/route_marker/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RouteMarkerViewSet

router = DefaultRouter()
router.register(r"route-markers", RouteMarkerViewSet, basename="routemarker")

urlpatterns = [
    path("", include(router.urls)),
]
