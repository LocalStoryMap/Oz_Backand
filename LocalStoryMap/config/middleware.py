from sentry_sdk import capture_exception

class LogAllErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code in [400, 403, 404, 405]:
            capture_exception(Exception(f"{response.status_code} Error on path: {request.path}"))

        return response