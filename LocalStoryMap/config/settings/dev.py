from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1','*']

# 개발용 URL 설정
ROOT_URLCONF = 'config.urls.urls_dev'

# DRF 기본 설정
REST_FRAMEWORK.update({
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
})

CORS_ALLOW_ALL_ORIGINS = True