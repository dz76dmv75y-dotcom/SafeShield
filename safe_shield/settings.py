"""
Django settings for safe_shield project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = 'django-insecure-!n89pzk!4iz2-i3hdm4q&y$b*^%fsye2nhu^!^ybv0k8q@p_h4'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'safeshield-v1db.onrender.com',
]


# Security settings

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # SafeShield Apps
    'accounts',
    'dashboard',
    'scanner',
    'protection',
    'passwords',
    'encryption',
    'threats',
    'reports',
    'academy',
    'notifications',
    'settings',
    'banking',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'safe_shield.middleware.ApplicationErrorLoggingMiddleware',
]


# =========================================================
# URL / WSGI
# =========================================================

ROOT_URLCONF = 'safe_shield.urls'

WSGI_APPLICATION = 'safe_shield.wsgi.application'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {

        'BACKEND':
            'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.template.context_processors.i18n',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

            ],

        },

    },

]


# =========================================================
# DATABASE
# =========================================================

DATABASES = {

    'default': {

        'ENGINE':
            'django.db.backends.sqlite3',

        'NAME':
            BASE_DIR / 'db.sqlite3',

    }

}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {

        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',

    },

    {

        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',

    },

]


# =========================================================
# PASSWORD HASHING
# =========================================================

PASSWORD_HASHERS = [

    'django.contrib.auth.hashers.Argon2PasswordHasher',

    'django.contrib.auth.hashers.PBKDF2PasswordHasher',

    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',

]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'

LANGUAGES = [

    ('en', 'English'),

    ('ar', 'العربية'),

]

LOCALE_PATHS = [

    BASE_DIR / 'locale'

]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [

    BASE_DIR / 'static',

]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================================================
# AUTHENTICATION
# =========================================================

AUTHENTICATION_BACKENDS = [

    'accounts.auth_backends.EmailOrUsernameBackend',

]

LOGIN_URL = 'accounts:login'

LOGIN_REDIRECT_URL = 'dashboard:home'

LOGOUT_REDIRECT_URL = 'home'


# =========================================================
# EMAIL
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'ضع_بريد_SCP_هنا'

EMAIL_HOST_PASSWORD = 'ضع_App_Password_هنا'


# =========================================================
# DEFAULT EMAIL
# =========================================================

DEFAULT_FROM_EMAIL = (
    'SCP - Smart Cyber Protection <safeshield.project@gmail.com>'
)


# =========================================================
# RESEND API
# =========================================================

RESEND_API_KEY = os.getenv(
    'RESEND_API_KEY'
)


# =========================================================
# DEFAULT AUTO FIELD
# =========================================================

DEFAULT_AUTO_FIELD = (
    'django.db.models.BigAutoField'
)