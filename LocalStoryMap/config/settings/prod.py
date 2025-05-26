from .base import *

try:
    from storages.backends.s3boto3 import S3Boto3Storage
except ImportError:
    S3Boto3Storage = None

# ---로그/정적 파일 디렉토리 설정--------------------------------
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(exist_ok=True)

static_dir = BASE_DIR / 'static'
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)

# ---프로덕션 설정---------------------------------------------
DEBUG = False
ROOT_URLCONF = 'config.urls.urls_prod'

# 도메인 설정
ALLOWED_HOSTS = [
    '223.130.152.69',
    'localhost',
    '127.0.0.1',
    'yourdomain.com',
    'www.yourdomain.com',
]

# ---PostgreSQL 설정------------------------------------------
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

# ---보안 설정--------------------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ---Storages 앱 추가-------------------------------------------
INSTALLED_APPS += [
    'storages',
]

# ---강제 S3 활성화 (조건문 제거)---------------------------------------------------------------------
USE_S3_STORAGE = os.getenv('USE_S3_STORAGE', 'False').lower() == 'true'

print(f"🔍 S3 설정 디버그: USE_S3_STORAGE={USE_S3_STORAGE}, 환경변수={os.getenv('USE_S3_STORAGE')}")

if USE_S3_STORAGE and S3Boto3Storage:
    print("🔥 S3 스토리지 활성화!")

    # S3 호환 Object Storage 설정
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # 네이버 클라우드 Object Storage 설정
    AWS_S3_ENDPOINT_URL = 'https://kr.object.ncloudstorage.com'
    AWS_ACCESS_KEY_ID = os.getenv('NCP_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('NCP_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('NCP_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'kr-standard'

    # 추가 S3 설정
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.kr.object.ncloudstorage.com'

    # URL 설정
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

    print(f"✅ S3 URL 설정: STATIC_URL={STATIC_URL}")

else:
    print("⚠️ S3 비활성화 - 로컬 스토리지 사용")
    # 로컬 파일 시스템 사용
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ---로깅 설정-------------------------------------------------------------------------------
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