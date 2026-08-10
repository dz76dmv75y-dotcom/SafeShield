import resend
from ipaddress import ip_address

from django.conf import settings
from django.core.mail import send_mail


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def is_private_ip(value):
    if not value:
        return False
    try:
        return ip_address(value).is_private
    except ValueError:
        return False


def send_email_message(subject, body, recipient_list, html_body=None):
    if getattr(settings, 'RESEND_API_KEY', None):
        try:
            resend.api_key = settings.RESEND_API_KEY
            message = {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": recipient_list,
                "subject": subject,
            }
            if html_body:
                message["html"] = html_body
            else:
                message["text"] = body

            response = resend.Emails.send(message)
            return response
        except Exception:
            # If Resend fails (for example unverified domain or API error),
            # fall back to Django SMTP mailer. Avoid exposing error details here.
            pass

    return send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
