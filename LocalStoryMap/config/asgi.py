import os

from channels.auth import AuthMiddlewareStack  # ✅ 반드시 필요
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import config.routing  # 👉 여기서 websocket_urlpatterns 로딩됨

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(  # ✅ 반드시 이게 있어야 scope["user"] 가능
            URLRouter(config.routing.websocket_urlpatterns)
        ),
    }
)
