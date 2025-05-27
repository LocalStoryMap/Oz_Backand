from pathlib import Path
import os
from dotenv import load_dotenv

# ─── .env 로드 ───────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)

# ─── 환경변수 기반 설정 ────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-if-not-set')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ROOT_URLCONF = 'config.urls'

# ─── 데이터 베이스 설정 ────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── 앱 등록 ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'storages',
]

# ─── 미들웨어 설정 ────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─── 템플릿 설정 ──────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 템플릿 디렉토리 추가
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ─── CORS 설정 (React 연동용) ──────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React 개발서버
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True


# ─── 비밀번호 검증 설정 ────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── 국제화 설정 ──────────────────────────────────────────
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# ─── 정적 파일 설정 ────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # 프로덕션용 정적 파일 수집 경로
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # 개발용 정적 파일 디렉토리
]

# ─── 스토리지 설정 (환경변수 기반) ────────────────────────
try:
    from storages.backends.s3boto3 import S3Boto3Storage
except ImportError:
    S3Boto3Storage = None

USE_S3_STORAGE = os.getenv('USE_S3_STORAGE', 'False').lower() == 'true'

if USE_S3_STORAGE and S3Boto3Storage:

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # 네이버 클라우드 Object Storage 설정
    AWS_S3_ENDPOINT_URL = 'https://kr.object.ncloudstorage.com'
    AWS_ACCESS_KEY_ID = os.getenv('NCP_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('NCP_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('NCP_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'kr-standard'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.kr.object.ncloudstorage.com'

    AWS_LOCATION = 'static/'
    AWS_MEDIA_LOCATION = 'media/'

    # S3 사용 시 STATIC_ROOT 제거 (충돌 방지)
    # STATIC_ROOT은 로컬 파일 시스템용이므로 S3 사용 시 불필요

    # URL 설정
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

    # 정적 파일 디렉토리는 유지 (개발용)
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]

else:
    print("📁 로컬 파일 시스템 사용 중...")

    # 로컬 파일 시스템 사용 (기본값)
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ─── 기본 설정 ────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── REST Framework 기본 설정 ─────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ─── 캐시 설정 ────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ─── 이메일 설정 (개발용 기본값) ────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ─── 로깅 기본 설정 ────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}