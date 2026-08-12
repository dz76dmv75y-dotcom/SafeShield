import os, sys
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_shield.settings')
import django
django.setup()
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

try:
    timestamp = int(timezone.now().timestamp())
    username = f"e2e_temp_{timestamp}"
    recipient = getattr(settings, 'TEST_RECIPIENT', None) or settings.EMAIL_HOST_USER

    user = User.objects.create_user(username=username, email=recipient, password='TempPwd!234')
    user.is_active = False
    user.save()
    print('CREATED')
    profile = user.profile
    otp = profile.generate_otp()
    print('OTP_GENERATED')

    # send via SMTP directly
    subject = 'SafeShield OTP direct SMTP test'
    body = 'This is a test message. Please ignore.'
    try:
        r = send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        print('SMTP_SEND_RESULT:' + str(r))
    except Exception as e:
        print('SMTP_SEND_ERROR:' + str(e))
        user.delete()
        sys.exit(2)

    # verify OTP server-side
    verified, err = profile.verify_otp(otp)
    if verified:
        print('VERIFY_OK')
    else:
        print('VERIFY_FAIL:' + str(err))

    user.delete()
    print('CLEANED')
except Exception as e:
    print('ERROR:' + str(e))
    sys.exit(1)
