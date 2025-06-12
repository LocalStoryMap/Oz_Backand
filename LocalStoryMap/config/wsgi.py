import os

from django.core.wsgi import get_wsgi_application

# 환경변수가 설정돼 있으면 그 값을, 없으면 dev를 기본값으로 사용
os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.dev",
)

application = get_wsgi_application()
