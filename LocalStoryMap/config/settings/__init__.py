

# 기본적으로 개발 환경 설정 사용
from config.settings.dev import *

# 환경 변수에 따라 배포 환경 설정 사용
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.prod':
    from config.settings.prod import *