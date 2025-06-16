INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "drf_yasg",
    # Local apps
    "apps.users.apps.UsersConfig",
    "apps.subscribes.apps.SubscribesConfig",
    "apps.paymenthistory.apps.PaymentHistoryConfig",  # 결제 이력 앱 추가
]
