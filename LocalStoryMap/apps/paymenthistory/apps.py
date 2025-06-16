from django.apps import AppConfig


class PaymentHistoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.paymenthistory"
    verbose_name = "결제 이력"
