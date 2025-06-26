import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import config.routing

# 1) 환경 설정 주입
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# 2) Django 앱 레지스트리 초기화
django.setup()

# 3) 앱 초기화 완료 후에 미들웨어 import
from apps.notifications.middleware import JWTAuthMiddleware

# 4) ASGI application 정의
application = ProtocolTypeRouter(
    {
        # HTTP 요청은 기본 ASGI 어플리케이션으로 처리
        "http": get_asgi_application(),
        # WebSocket 요청은 JWTAuthMiddleware로 래핑한 URLRouter로 처리
        "websocket": JWTAuthMiddleware(URLRouter(config.routing.websocket_urlpatterns)),
    }
)
