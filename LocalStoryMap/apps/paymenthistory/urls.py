from django.urls import path

from .apis import PaymentHistoryDetailAPIView, PaymentHistoryListAPIView

app_name = "paymenthistory"

urlpatterns = [
    path("", PaymentHistoryListAPIView.as_view(), name="payment-history-list"),
    path(
        "<int:payment_id>/",
        PaymentHistoryDetailAPIView.as_view(),
        name="payment-history-detail",
    ),
] 