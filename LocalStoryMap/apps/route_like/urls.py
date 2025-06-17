# apps/route_like/urls.py
from django.urls import path

from .views import RouteLikeViewSet

route_like_list = RouteLikeViewSet.as_view({"get": "list"})
route_like_status = RouteLikeViewSet.as_view({"get": "like_status"})
route_like_toggle = RouteLikeViewSet.as_view({"post": "toggle_like"})

urlpatterns = [
    path("routes/<int:route_id>/likes/", route_like_list, name="route-like-list"),
    path(
        "routes/<int:route_id>/likes/status/",
        route_like_status,
        name="route-like-status",
    ),
    path(
        "routes/<int:route_id>/likes/toggle/",
        route_like_toggle,
        name="route-like-toggle",
    ),
]
