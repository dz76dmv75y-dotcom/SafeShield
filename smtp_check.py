import os
import sys
import smtplib
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safe_shield.settings')
import django
django.setup()

host = settings.EMAIL_HOST
port = settings.EMAIL_PORT
use_tls = settings.EMAIL_USE_TLS
use_ssl = settings.EMAIL_USE_SSL
user = settings.EMAIL_HOST_USER
password = settings.EMAIL_HOST_PASSWORD

try:
    if use_ssl:
        server = smtplib.SMTP_SSL(host, port, timeout=15)
    else:
        server = smtplib.SMTP(host, port, timeout=15)
    server.ehlo()
    if use_tls:
        server.starttls()
        server.ehlo()
    try:
        server.login(user, password)
        print('SMTP_LOGIN_OK')
    except smtplib.SMTPAuthenticationError as e:
        print('SMTP_AUTH_ERROR')
        # non-sensitive detail
        print('AUTH_ERR_CODE:' + str(getattr(e, 'smtp_code', '')))
    except Exception as e:
        print('SMTP_LOGIN_ERROR:' + str(e))
    finally:
        try:
            server.quit()
        except Exception:
            pass
except Exception as e:
    print('SMTP_CONNECT_ERROR:' + str(e))
    sys.exit(1)
