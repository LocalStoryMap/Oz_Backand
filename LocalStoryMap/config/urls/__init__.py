import os

# 기본적으로 개발 환경 URL 설정을 사용
env = os.environ.get('DJANGO_ENV', 'dev')

if env == 'production' or env == 'prod':
    from .urls_prod import urlpatterns
else:
    from .urls_dev import urlpatterns