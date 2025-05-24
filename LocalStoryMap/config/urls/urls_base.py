from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    # Django 관리자 페이지
    path('admin/', admin.site.urls),

    # REST Framework URL
    path('api/', include(router.urls)),

    # REST Framework 인증 URL
    path('api-auth/', include('rest_framework.urls')),
]

# 개발 환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # 개발 환경에서만 정적 파일 서빙 (필요한 경우)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)