import os
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_shield.settings')
import django
django.setup()
from django.core.mail import send_mail

subject = 'SafeShield simple send test'
message = 'This is a simple SMTP send test from SafeShield.'
recipient = getattr(settings, 'TEST_RECIPIENT', None) or settings.EMAIL_HOST_USER

try:
    result = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    print('SEND_MAIL_RETURN:' + str(result))
except Exception as e:
    print('SEND_MAIL_ERROR:' + str(e))
