import os
import sys
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_shield.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from accounts.utils import send_email_message

try:
    timestamp = int(timezone.now().timestamp())
    username = f"e2e_test_user_{timestamp}"
    email = getattr(settings, 'TEST_RECIPIENT', None) or settings.EMAIL_HOST_USER

    # Create temporary user
    user = User.objects.create_user(username=username, email=email, password='TemporaryPass!234')
    user.is_active = False
    user.save()

    print('CREATED_USER')

    profile = user.profile

    # Generate OTP (returned value will not be printed)
    otp = profile.generate_otp()
    print('GENERATED_OTP')

    # Send email using project's configured helper
    try:
        resp = send_email_message(
            subject="SafeShield OTP E2E Test",
            body="This is a test of SafeShield OTP delivery.",
            recipient_list=[email],
        )
    except Exception as e:
        print("SEND_ERROR:" + str(e))
        # cleanup
        try:
            user.delete()
        except Exception:
            pass
        sys.exit(2)
    print('SENT_EMAIL')

    # Inspect response in a non-sensitive way
    send_ok = False
    try:
        # SMTP path returns an int number of emails sent
        if isinstance(resp, int):
            if resp >= 1:
                print("SEND_OK_SMTP")
                send_ok = True
            else:
                print("SEND_NO_DELIVERY")
        else:
            # Resend or API client may return objects/dicts
            # Check for common signals without printing any secrets
            if hasattr(resp, 'id'):
                print("SEND_OK_RESEND")
                send_ok = True
            elif isinstance(resp, dict) and resp.get('id'):
                print("SEND_OK_RESEND")
                send_ok = True
            else:
                print("SEND_RESPONSE_UNKNOWN: %s" % (type(resp),))
    except Exception as e:
        print("SEND_RESPONSE_ERROR:" + str(e))

    # Verify OTP using server-side verify method (do not expose OTP)
    try:
        verified, err = profile.verify_otp(otp)
        if verified:
            print("VERIFY_OK")
        else:
            print("VERIFY_FAIL:" + str(err))
    except Exception as e:
        print("VERIFY_ERROR:" + str(e))

    # Cleanup temporary user
    try:
        user.delete()
        print("CLEANUP_OK")
    except Exception as e:
        print("CLEANUP_ERROR:" + str(e))
        sys.exit(3)

    # Run manage.py check programmatically
    from django.core.management import call_command
    try:
        call_command('check')
        print('MANAGE_CHECK_OK')
    except Exception as e:
        print('MANAGE_CHECK_ERROR:' + str(e))
        sys.exit(4)

except Exception as e:
    print('E2E_SCRIPT_ERROR:' + str(e))
    sys.exit(1)
