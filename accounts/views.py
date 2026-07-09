from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from notifications.models import Notification

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import ApplicationErrorLog, Profile, SecurityLog
from .utils import get_client_ip


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.verification_token = profile.verification_token or 'demo-token'
            profile.save(update_fields=['verification_token'])
            verification_url = request.build_absolute_uri(reverse('accounts:verify-email', args=[profile.verification_token]))
            from django.core.mail import send_mail
            send_mail(
                'Verify your SafeShield account',
                f'Hello {user.username}, verify your account here: {verification_url}',
                'noreply@safeshield.local',
                [user.email],
                fail_silently=True,
            )
            Notification.objects.create(user=user, title='Welcome to SafeShield', body='Your account is nearly ready. Verify your email to unlock all protection features.', category='welcome')
            Notification.objects.create(user=user, title='Security Setup', body='Complete your profile and enable real-time protection to start securing your digital identity.', category='security')
            SecurityLog.objects.create(
                user=user,
                event_type='account_created',
                title=_('New account created'),
                details=_('A new SafeShield account was registered and is ready for security monitoring.'),
                severity='info',
                source='Registration',
                ip_address=get_client_ip(request),
            )
            messages.success(request, _('Account created. Check your inbox for the verification link.'))
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile = user.profile
            profile.reset_login_tracking()
            profile.last_login_ip = get_client_ip(request)
            profile.last_login_at = user.last_login
            profile.save(update_fields=['failed_login_count', 'locked_until', 'last_login_ip', 'last_login_at'])
            SecurityLog.objects.create(
                user=user,
                event_type='login_success',
                title=_('Successful login'),
                details=_('The user signed in successfully using the SafeShield authentication flow.'),
                severity='info',
                source='Authentication',
                ip_address=get_client_ip(request),
            )
            if not getattr(user.profile, 'email_verified', False):
                messages.info(request, _('You signed in successfully. Please verify your email later to strengthen account protection.'))
            else:
                messages.success(request, _('Signed in successfully.'))
            return redirect('dashboard:home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        SecurityLog.objects.create(
            user=request.user,
            event_type='login_success',
            title=_('User signed out'),
            details=_('The user ended their session safely.'),
            severity='info',
            source='Authentication',
            ip_address=get_client_ip(request),
        )
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('home')


def verify_email(request, token):
    profile = Profile.objects.filter(verification_token=token).first()
    if profile:
        profile.email_verified = True
        profile.verification_token = ''
        profile.save(update_fields=['email_verified', 'verification_token'])
        profile.user.is_active = True
        profile.user.save(update_fields=['is_active'])
        SecurityLog.objects.create(
            user=profile.user,
            event_type='account_created',
            title=_('Email verified'),
            details=_('The user verified their email address and activated the account.'),
            severity='info',
            source='Verification',
            ip_address=get_client_ip(request),
        )
        messages.success(request, _('Email verified successfully. You can now sign in.'))
    else:
        messages.error(request, _('The provided verification link is invalid or expired.'))
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile.phone = form.cleaned_data['phone']
            profile.company = form.cleaned_data['company']
            profile.location = form.cleaned_data['location']
            profile.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('accounts:profile')
    else:
        form = ProfileForm(initial={'phone': profile.phone, 'company': profile.company, 'location': profile.location})
    return render(request, 'accounts/profile.html', {'profile': profile, 'form': form})


@staff_member_required
def admin_dashboard(request):
    users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    security_logs = SecurityLog.objects.order_by('-created_at')[:10]
    error_logs = ApplicationErrorLog.objects.order_by('-created_at')[:10]
    failed_login_count = SecurityLog.objects.filter(event_type='failed_login').count()
    context = {
        'users': users,
        'staff_users': staff_users,
        'security_logs': security_logs,
        'error_logs': error_logs,
        'failed_login_count': failed_login_count,
    }
    return render(request, 'accounts/admin_dashboard.html', context)
