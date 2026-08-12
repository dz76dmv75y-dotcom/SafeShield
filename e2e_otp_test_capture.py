import os
import sys
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_shield.settings')
# Force SMTP path for this endpoint test so we validate the configured mailer directly.
os.environ['RESEND_API_KEY'] = ''
import django
django.setup()
from django.conf import settings
from django.contrib.auth.models import User
from accounts.utils import send_email_message

log_path = os.path.join(os.path.dirname(__file__), 'e2e_otp_log.txt')

with open(log_path, 'w', encoding='utf-8') as log:
    def log_print(value):
        log.write(value + '\n')
        log.flush()

    try:
        timestamp = int(timezone.now().timestamp())
        username = f"e2e_test_user_{timestamp}"
        email = getattr(settings, 'TEST_RECIPIENT', None) or settings.EMAIL_HOST_USER

        user = User.objects.create_user(username=username, email=email, password='TemporaryPass!234')
        user.is_active = False
        user.save()
        log_print('CREATED_USER')

        profile = user.profile
        otp = profile.generate_otp()
        log_print('GENERATED_OTP')

        try:
            resp = send_email_message(
                subject='SafeShield OTP E2E Test',
                body='This is a test of SafeShield OTP delivery.',
                recipient_list=[email],
            )
            log_print('EMAIL_SEND_ATTEMPTED')
        except Exception as e:
            log_print('SEND_ERROR')
            log_print(str(type(e)))
            try:
                user.delete()
            except Exception:
                pass
            sys.exit(2)

        if isinstance(resp, int):
            log_print(f'SEND_RESULT_INT:{resp}')
        elif hasattr(resp, 'id'):
            log_print('SEND_RESULT_RESEND_ID')
        elif isinstance(resp, dict) and resp.get('id'):
            log_print('SEND_RESULT_RESEND_DICT')
        else:
            log_print(f'SEND_RESULT_UNKNOWN:{type(resp)}')

        verified, err = profile.verify_otp(otp)
        if verified:
            log_print('VERIFY_OK')
        else:
            log_print(f'VERIFY_FAIL:{err}')

        try:
            user.delete()
            log_print('CLEANUP_OK')
        except Exception as e:
            log_print('CLEANUP_ERROR')
            log_print(str(type(e)))
            sys.exit(3)

        from django.core.management import call_command
        try:
            call_command('check')
            log_print('MANAGE_CHECK_OK')
        except Exception as e:
            log_print('MANAGE_CHECK_ERROR')
            log_print(str(type(e)))
            sys.exit(4)

    except Exception as e:
        log_print('E2E_SCRIPT_ERROR')
        log_print(str(type(e)))
        sys.exit(1)
