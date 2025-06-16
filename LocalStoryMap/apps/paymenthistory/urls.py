from django.urls import path

from .apis import PaymentHistoryDetailAPIView, PaymentHistoryListAPIView

app_name = "paymenthistory"

urlpatterns = [
    # 결제 이력 목록 조회
    path("", PaymentHistoryListAPIView.as_view(), name="payment_history_list"),
    # 결제 이력 상세 조회 및 삭제
    path(
        "<int:payment_id>/",
        PaymentHistoryDetailAPIView.as_view(),
        name="payment-history-detail",
    ),
]
