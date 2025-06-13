from rest_framework.views import exception_handler as drf_exception_handler
from sentry_sdk import capture_exception


def custom_exception_handler(exc, context):
    # 기본 DRF 예외 핸들링
    response = drf_exception_handler(exc, context)

    # 모든 예외를 Sentry에 기록 (심지어 ValidationError 포함)
    capture_exception(exc)

    return response
