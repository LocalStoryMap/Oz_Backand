import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import config.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(config.routing.websocket_urlpatterns),
    }
)
