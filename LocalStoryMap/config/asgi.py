import os

from dotenv import load_dotenv

load_dotenv()  # .env 환경변수 로드

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import config.routing

os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.dev",
)

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(config.routing.websocket_urlpatterns)
        ),
    }
)
