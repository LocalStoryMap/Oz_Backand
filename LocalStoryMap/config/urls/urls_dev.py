from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .urls_base import urlpatterns as base_urlpatterns

# 개발용 URL 구성은 base와 동일하게 사용
urlpatterns = base_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="1LLO1LLO",
        default_version="v1",
        description="1LLO1LLO 프로젝트 API 문서",
        contact=openapi.Contact(email="email@email.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from django.urls import path

urlpatterns += [
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
