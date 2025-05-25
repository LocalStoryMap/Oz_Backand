from .base import *

# 로그/정적 파일 디렉토리 설정
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(exist_ok=True)

static_dir = BASE_DIR / 'static'
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)

# 프로덕션 설정
DEBUG = False
ROOT_URLCONF = 'config.urls.urls_prod'

# 도메인 설정
ALLOWED_HOSTS = [
    '223.130.152.69',  # 서버 IP
    'localhost',
    '127.0.0.1',
    'yourdomain.com',
    'www.yourdomain.com',
]

# 네이버 클라우드 PostgreSQL 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NCP_DB_NAME'),
        'USER': os.getenv('NCP_DB_USER'),
        'PASSWORD': os.getenv('NCP_DB_PASSWORD'),
        'HOST': os.getenv('NCP_DB_HOST'),
        'PORT': os.getenv('NCP_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'disable',
        },
    }
}

# 보안 설정 (개발 서버용)
SECURE_SSL_REDIRECT = False  # HTTP 허용
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 로깅 설정
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