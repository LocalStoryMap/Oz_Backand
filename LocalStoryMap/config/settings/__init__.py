import os

# 기본적으로 프로덕션 환경 설정을 사용하고,
# 명시적으로 'dev'로 지정된 경우에만 개발 환경 사용
env = os.environ.get('DJANGO_ENV', 'prod')

if env == 'dev' or env == 'development':
    from .dev import *
else:
    from .prod import *