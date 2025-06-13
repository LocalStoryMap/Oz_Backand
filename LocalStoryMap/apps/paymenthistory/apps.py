from django.apps import AppConfig


class PaymentHistoryConfig(AppConfig):
    """결제 이력 앱 설정"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.paymenthistory"
    verbose_name = "결제 이력"
