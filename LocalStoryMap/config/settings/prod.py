from .base import *

# ---로그/정적 파일 디렉토리 설정----------------------------------
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(exist_ok=True)

static_dir = BASE_DIR / 'static'
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)

# ---프로덕션 설정-----------------------------------------------
DEBUG = False
ROOT_URLCONF = 'config.urls.urls_prod'

# ---CORS 설정 (프로덕션용)---------------------------------------
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",      # ✅ 실제 도메인으로 변경
    "https://www.yourdomain.com",
]

# ---도메인 설정-------------------------------------------------
ALLOWED_HOSTS = [
    '223.130.152.69',
    'localhost',
    '127.0.0.1',
    'yourdomain.com',
    'www.yourdomain.com',
]

# ---PostgreSQL 설정---------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NCP_DB_NAME'),
        'USER': os.getenv('NCP_DB_USER'),
        'PASSWORD': os.getenv('NCP_DB_PASSWORD'),
        'HOST': os.getenv('NCP_DB_HOST'),
        'PORT': os.getenv('NCP_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 60,
    }
}

# ---보안 설정------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# 추가 보안 설정
SECURE_HSTS_SECONDS = 31536000  # 1년 (HTTPS 강제)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True  # 클릭재킹 방지
X_FRAME_OPTIONS = 'DENY'

# 성능 최적화
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# ---Redis 캐시 설정 (성능 향상)----------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# ---로깅 설정--------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': logs_dir / 'error.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}