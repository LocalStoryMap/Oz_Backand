from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger 문서 설정
schema_view = get_schema_view(
    openapi.Info(
        title="LocalStoryMap API",
        default_version="v1",
        description="LocalStoryMap 백엔드 API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@localstorymap.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API
    path("api/users/", include("apps.users.urls")),
    path("api/subscribes/", include("apps.subscribes.urls")),
    path("api/payment-histories/", include("apps.paymenthistory.urls")),
    # Swagger 문서
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
