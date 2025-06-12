from django.urls import path

from .apis import SubscribeDetailAPIView, SubscribeListCreateAPIView

app_name = "subscribes"

urlpatterns = [
    path(
        "",
        SubscribeListCreateAPIView.as_view(),
        name="subscribe-list-create",
    ),
    path(
        "<int:subscribe_id>/",
        SubscribeDetailAPIView.as_view(),
        name="subscribe-detail",
    ),
]
