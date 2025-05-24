from .urls_base import urlpatterns as base_urlpatterns
from django.urls import URLPattern

urlpatterns = [
    url for url in base_urlpatterns
    if not (
        isinstance(url, URLPattern) and url.name in ['schema', 'swagger-ui', 'redoc']
    )
]

