from config.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 개발용 SQLite 데이터베이스
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DRF 기본 설정
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}
