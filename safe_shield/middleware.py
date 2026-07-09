import traceback

from django.http import Http404

from accounts.models import ApplicationErrorLog
from accounts.utils import get_client_ip


class ApplicationErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return None
        user = getattr(request, 'user', None)
        ApplicationErrorLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            path=getattr(request, 'path', ''),
            message=str(exception),
            traceback=''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
            ip_address=get_client_ip(request),
        )
        return None
