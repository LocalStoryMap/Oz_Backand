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
    'yourdomain.com',
    'www.yourdomain.com',
    # 개발 중인 경우 추가
    'localhost',
    '127.0.0.1',
]

# 네이버 클라우드 PostgreSQL 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NCP_DB_NAME'),
        'USER': os.getenv('NCP_DB_USER'),
        'PASSWORD': os.getenv('NCP_DB_PASSWORD'),
        'HOST': os.getenv('NCP_DB_HOST'),  # NCP 엔드포인트
        'PORT': os.getenv('NCP_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'disable',  # SSL 연결 활성화 (필요한 경우)
            'options': '-c search_path=public',
        },
    }
}

# 나머지 프로덕션 설정...
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 로깅 설정...
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

