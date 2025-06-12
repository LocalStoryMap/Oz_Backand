import os

from dotenv import load_dotenv

load_dotenv()  # .env 환경변수 로드

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.dev",
)

application = get_wsgi_application()
