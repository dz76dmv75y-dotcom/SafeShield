from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import SecurityLog
from .utils import get_client_ip


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        users = UserModel._default_manager.filter(Q(username__iexact=username) | Q(email__iexact=username))
        for user in users:
            profile = getattr(user, 'profile', None)
            if profile and profile.is_locked():
                SecurityLog.objects.create(
                    user=user,
                    event_type='failed_login',
                    title='Account locked due to repeated failures',
                    details='The account is temporarily locked after repeated failed login attempts.',
                    severity='high',
                    source='Authentication',
                    ip_address=get_client_ip(request) if request else None,
                )
                return None
            if user.check_password(password) and self.user_can_authenticate(user):
                if profile:
                    profile.reset_login_tracking()
                    profile.last_login_ip = get_client_ip(request) if request else None
                    profile.last_login_at = user.last_login
                    profile.save(update_fields=['failed_login_count', 'locked_until', 'last_login_ip', 'last_login_at'])
                SecurityLog.objects.create(
                    user=user,
                    event_type='login_success',
                    title='Successful login',
                    details='The user signed in successfully using the secure authentication backend.',
                    severity='info',
                    source='Authentication',
                    ip_address=get_client_ip(request) if request else None,
                )
                return user

            if profile:
                profile.record_failed_login()
                SecurityLog.objects.create(
                    user=user,
                    event_type='failed_login',
                    title='Failed login attempt',
                    details='An incorrect password or invalid credentials were provided.',
                    severity='medium',
                    source='Authentication',
                    ip_address=get_client_ip(request) if request else None,
                )
        return None
