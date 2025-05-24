from config.urls.urls_base import urlpatterns as base_urlpatterns
from django.urls.resolvers import URLPattern

urlpatterns = [
    url for url in base_urlpatterns
    if not (
        isinstance(url, URLPattern) and url.name in ['schema', 'swagger-ui', 'redoc']
    )
]
