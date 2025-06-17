# apps/marker_like/urls.py
from django.urls import path

from .views import MarkerLikeViewSet

marker_like_list = MarkerLikeViewSet.as_view({"get": "list"})
marker_like_status = MarkerLikeViewSet.as_view({"get": "like_status"})
marker_like_toggle = MarkerLikeViewSet.as_view({"post": "toggle_like"})

urlpatterns = [
    path("markers/<int:marker_id>/likes/", marker_like_list, name="marker-like-list"),
    path(
        "markers/<int:marker_id>/likes/status/",
        marker_like_status,
        name="marker-like-status",
    ),
    path(
        "markers/<int:marker_id>/likes/toggle/",
        marker_like_toggle,
        name="marker-like-toggle",
    ),
]
