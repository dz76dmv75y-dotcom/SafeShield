import logging
import traceback

from django.http import Http404

from accounts.models import ApplicationErrorLog
from accounts.utils import get_client_ip


logger = logging.getLogger(__name__)


class ApplicationErrorLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):

        # تجاهل أخطاء 404
        if isinstance(exception, Http404):
            return None

        try:

            user = getattr(request, "user", None)

            ApplicationErrorLog.objects.create(

                user=(
                    user
                    if getattr(user, "is_authenticated", False)
                    else None
                ),

                path=getattr(
                    request,
                    "path",
                    ""
                ),

                message=str(exception),

                traceback="".join(
                    traceback.format_exception(
                        type(exception),
                        exception,
                        exception.__traceback__,
                    )
                ),

                ip_address=get_client_ip(request),

            )

        except Exception:

            # إذا فشل تسجيل الخطأ،
            # لا نريد أن يسبب هذا خطأ 500 جديد
            logger.exception(
                "Failed to save application error log."
            )

        # السماح لـ Django بمعالجة الخطأ الأصلي
        return None