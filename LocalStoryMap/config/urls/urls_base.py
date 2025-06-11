from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

# 헬스체크용 뷰


def health(request):
    return JsonResponse({"status": "ok"})


# API 라우터 설정
router = DefaultRouter()

# 나중에 ViewSet 추가시 여기에 등록
# router.register(r'users', UserViewSet)
# router.register(r'posts', PostViewSet)


# ─── Swagger 설정 ──────────────────────────────────────────
schema_view = get_schema_view(
    openapi.Info(
        title="1LLO1LLO",
        default_version="v1",
        description="1LLO1LLO 프로젝트 RESTful API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="email@email.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # 건강 상태 확인───────────────────────────────────────────────────
    path("health/", health),
    # ── Admin ─────────────────────────────────────────────────────
    path("admin/", admin.site.urls),
    # ── Versioned API Endpoints ───────────────────────────────────
    path("api/v1/", include(router.urls)),
    # ── Backward-compatible Unversioned API ──────────────────────
    path("api/", include(router.urls)),
    # ── Authentication ────────────────────────────────────────────
    path("api-auth/", include("rest_framework.urls")),
    path("token/", obtain_auth_token, name="api_token_auth"),
    # ── Application Endpoints ────────────────────────────────────
    path("users/", include("apps.users.urls", namespace="users")),
    path(
        "notifications/",
        include(
            "apps.notifications.urls",
        ),
    ),
    path("follows/", include("apps.follows.urls")),
    path("search/", include("apps.search.urls")),
    # ── AI Service Endpoints ─────────────────────────────────────
    path("Ai/", include("ai_service.urls")),
    # ── API Documentation ────────────────────────────────────────
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("", include("apps.marker.urls")),
    path("", include("apps.route.urls")),
    path("api/", include("apps.route_marker.urls")),
]

# ─── DEBUG 모드에서만 Debug Toolbar URL 추가 ───────────────
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

# 개발 환경에서만 파일 서빙
if settings.DEBUG:
    # 미디어 파일 서빙
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # 정적 파일 서빙 (개발용)
    if hasattr(settings, "STATICFILES_DIRS") and settings.STATICFILES_DIRS:
        urlpatterns += static(
            settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
        )
    else:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
