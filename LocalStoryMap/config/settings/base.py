import os
from pathlib import Path

from dotenv import load_dotenv

# ─── .env 로드 ───────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ─── Sentry SDK 초기화 ───────────────────────────────────────
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_RELEASE = os.getenv("SENTRY_RELEASE")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=os.getenv("DJANGO_ENV", "prod"),  # dev/ prod 구분
        release=SENTRY_RELEASE,  # 커밋 SHA 또는 태그와 매핑
        # traces_sample_rate=1.0,  # 필요 시 APM 추적 옵션
    )

# ─── 환경변수 기반 설정 ────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-if-not-set")
DEBUG = True
ROOT_URLCONF = "config.urls"

# ─── S3(Object Storage) 환경변수 매핑 ───────────────────────
AWS_ACCESS_KEY_ID = os.getenv("NCP_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("NCP_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("NCP_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv(
    "AWS_S3_ENDPOINT_URL", "https://kr.object.ncloudstorage.com"
)
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "kr-standard")
AWS_S3_ADDRESSING_STYLE = "path"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.kr.object.ncloudstorage.com"
    if AWS_STORAGE_BUCKET_NAME
    else None
)
AWS_LOCATION = "static/"
AWS_MEDIA_LOCATION = "media/"

# ─── 데이터베이스 설정 ─────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ─── 앱 등록 ─────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "storages",
    # myapp
    "ai_service",  # 요약/챗봇 기능을 담당할 앱
    "drf_yasg",
]

AUTH_USER_MODEL = "users.User"
# ─── DEBUG 모드에서만 Debug Toolbar를 등록 ───────────────────
if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

# ─── 미들웨어 설정 ────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─── Debug Toolbar 미들웨어 (Debug 모드일 때만) ──────────────
if DEBUG:
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

# ─── INTERNAL_IPS 설정 (Debug Toolbar 표시할 IP) ────────────
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
        # Docker 환경 등에서 외부 IP가 다를 경우 필요한 IP를 추가하세요.
    ]

# ─── 템플릿 설정 ──────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─── CORS 설정 (React 연동용) ──────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# ─── 비밀번호 검증 설정 ────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── 국제화 설정 ──────────────────────────────────────────
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# ─── 스토리지 설정 (환경변수 기반) ────────────────────────
USE_S3_STORAGE = os.getenv("USE_S3_STORAGE", "False").lower() == "true"

if (
    USE_S3_STORAGE
    and AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY
    and AWS_STORAGE_BUCKET_NAME
):
    # ─── Static/Media ────────────────────────────────────────────────
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # S3 URL 설정
    STATIC_URL = "/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}"

    # 로컬 정적 디렉토리(개발용) 설정
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [BASE_DIR / "static"]
    MEDIA_ROOT = BASE_DIR / "media"
else:
    # ─── Static은 로컬에서 서빙, Media만 S3에 저장 ─────────────────
    # 1) Static (로컬 디스크)
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    # 2) Media (업로드된 파일만 S3로)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}"
    MEDIA_ROOT = BASE_DIR / "media"

# ─── 기본 설정 ────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── REST Framework 기본 설정 ─────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "config.renderers.CamelCaseJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

from datetime import timedelta

# 카카오 로그인 시에 JWT를 발급하기 위한 Simple JWT 설정
SIMPLE_JWT = {
    # 토큰 만료 기간(ex: Access 5분, Refresh 14일)
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # Django의 SECRET_KEY를 그대로 사용
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "")

GOOGLE_OAUTH2_CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID", "")
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH2_CLIENT_SECRET", "")
GOOGLE_OAUTH2_REDIRECT_URI = os.getenv(
    "GOOGLE_OAUTH2_REDIRECT_URI", "http://127.0.0.1:8000/users/login/google/callback/"
)

# ─── 캐시 설정 ────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# ─── 이메일 설정 (개발용) ─────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── 로깅 설정 ───────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Clova Studio 환경변수
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY", "")  # 반드시 값 있어야 함
CLOVA_STUDIO_SKILL_ID = os.getenv("CLOVA_STUDIO_SKILL_ID", "")
CLOVA_STUDIO_BASE_URL = os.getenv(
    "CLOVA_STUDIO_BASE_URL", "https://clovastudio.stream.ntruss.com/testapp/v1"
)

# Clova Chat-completions URL 구성 (기본 형식)
# 예) https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003
CLOVA_CHAT_COMPLETIONS_URL = (
    f"{CLOVA_STUDIO_BASE_URL}/chat-completions/{CLOVA_STUDIO_SKILL_ID}"
)
