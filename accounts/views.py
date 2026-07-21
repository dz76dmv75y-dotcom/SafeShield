from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.conf import settings

from reportlab.pdfgen import canvas
from notifications.models import Notification

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import ApplicationErrorLog, Profile, SecurityLog
from .utils import get_client_ip

import resend

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            profile = user.profile
            profile.verification_token = profile.verification_token or 'demo-token'
            profile.save(update_fields=['verification_token'])

            verification_url = request.build_absolute_uri(
                reverse('accounts:verify-email', args=[profile.verification_token])
            )

            from django.core.mail import send_mail

            send_mail(
                'Verify your SafeShield account',
                f'Hello {user.username}, verify your account here: {verification_url}',
                'noreply@safeshield.local',
                [user.email],
                fail_silently=True,
            )

            Notification.objects.create(
                user=user,
                title='Welcome to SafeShield',
                body='Your account is nearly ready.',
                category='welcome'
            )

            SecurityLog.objects.create(
                user=user,
                event_type='account_created',
                title=_('New account created'),
                details=_('A new SafeShield account was registered.'),
                severity='info',
                source='Registration',
                ip_address=get_client_ip(request),
            )

            messages.success(request, _('Account created successfully.'))
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
            profile.save(
                update_fields=[
                    'failed_login_count',
                    'locked_until',
                    'last_login_ip',
                    'last_login_at'
                ]
            )

            SecurityLog.objects.create(
                user=user,
                event_type='login_success',
                title=_('Successful login'),
                details=_('User logged in successfully.'),
                severity='info',
                source='Authentication',
                ip_address=get_client_ip(request),
            )

            messages.success(request, _('Signed in successfully.'))
            return redirect('dashboard:home')


        else:
            username = request.POST.get('username')

            user = User.objects.filter(username=username).first()

            if user:

                user.profile.record_failed_login()

                SecurityLog.objects.create(
                    user=user,
                    event_type='failed_login',
                    title=_('Failed login attempt'),
                    details=_('A failed login attempt was detected.'),
                    severity='warning',
                    source='Authentication',
                    ip_address=get_client_ip(request),
                )


    else:
        form = LoginForm()


    return render(request, 'accounts/login.html', {'form': form})



def logout_view(request):

    if request.user.is_authenticated:

        SecurityLog.objects.create(
            user=request.user,
            event_type='login_success',
            title=_('User signed out'),
            details=_('User ended the session safely.'),
            severity='info',
            source='Authentication',
            ip_address=get_client_ip(request),
        )

    logout(request)

    messages.info(request, _('You have been logged out.'))

    return redirect('home')



def verify_email(request, token):

    profile = Profile.objects.filter(
        verification_token=token
    ).first()


    if profile:

        profile.email_verified = True
        profile.verification_token = ''

        profile.save(
            update_fields=[
                'email_verified',
                'verification_token'
            ]
        )

        profile.user.is_active = True
        profile.user.save(
            update_fields=['is_active']
        )


        SecurityLog.objects.create(
            user=profile.user,
            event_type='account_created',
            title=_('Email verified'),
            details=_('User verified email address.'),
            severity='info',
            source='Verification',
            ip_address=get_client_ip(request),
        )


        messages.success(
            request,
            _('Email verified successfully.')
        )

    else:

        messages.error(
            request,
            _('Invalid verification link.')
        )


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

            messages.success(
                request,
                _('Profile updated successfully.')
            )

            return redirect('accounts:profile')


    else:

        form = ProfileForm(
            initial={
                'phone': profile.phone,
                'company': profile.company,
                'location': profile.location
            }
        )


    return render(
        request,
        'accounts/profile.html',
        {
            'profile': profile,
            'form': form
        }
    )



@staff_member_required
def admin_dashboard(request):

    users = User.objects.count()

    staff_users = User.objects.filter(
        is_staff=True
    ).count()

    security_logs = SecurityLog.objects.order_by(
        '-created_at'
    )[:10]


    error_logs = ApplicationErrorLog.objects.order_by(
        '-created_at'
    )[:10]


    failed_login_count = SecurityLog.objects.filter(
        event_type='failed_login'
    ).count()


    context = {

        'users': users,

        'staff_users': staff_users,

        'security_logs': security_logs,

        'error_logs': error_logs,

        'failed_login_count': failed_login_count,

    }


    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )

@login_required
def security_dashboard(request):
    profile = request.user.profile

    security_logs = SecurityLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'security_score': profile.security_score,
        'last_login_ip': profile.last_login_ip,
        'last_login_at': profile.last_login_at,
        'security_logs': security_logs,
    }

    return render(
        request,
        'accounts/security_dashboard.html',
        context
    )
@login_required
def start_security_scan(request):
    profile = request.user.profile

    score = 100

    if not profile.email_verified:
        score -= 20

    if profile.failed_login_count > 0:
        score -= 10

    profile.security_score = score
    profile.save(update_fields=['security_score'])

    SecurityLog.objects.create(
        user=request.user,
        event_type='suspicious_activity',
        title='Security Scan Completed',
        details='Security scan completed successfully.',
        severity='info',
        source='Security Scanner',
        ip_address=get_client_ip(request),
    )

    messages.success(request, 'Security scan completed successfully.')

    return redirect('accounts:security-dashboard')

@login_required
def security_report(request):

    profile = request.user.profile

    security_logs = SecurityLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    return render(
        request,
        "accounts/security_report.html",
        {
            "user": request.user,
            "profile": profile,
            "security_logs": security_logs,
        }
    )

def test_scp_email(request):
    resend.api_key = settings.RESEND_API_KEY

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": ["safeshield.project@gmail.com"],
        "subject": "SCP - Smart Cyber Protection | Test Email",
        "html": """
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            text-align: center;
            border: 1px solid #ddd;
            border-radius: 15px;
        ">

            <div style="font-size: 60px;">
                🛡️
            </div>

            <h1>SCP</h1>

            <h2>Smart Cyber Protection</h2>

            <hr>

            <h3>اختبار نظام البريد الإلكتروني</h3>

            <p>
                هذه رسالة تجريبية من نظام الحماية الذكي
                Smart Cyber Protection.
            </p>

            <p>
                إذا وصلتك هذه الرسالة، فهذا يعني أن
                نظام البريد الإلكتروني يعمل بنجاح.
            </p>

            <br>

            <p>
                🛡️ حماية ذكية لعالم رقمي أكثر أمانًا
            </p>

            <hr>

            <small>
                Smart Cyber Protection © 2026
            </small>

        </div>
        """,
    })

    return HttpResponse(
        "SCP email test sent successfully!"
    )
@login_required
def download_security_report(request):
    profile = request.user.profile
    security_logs = SecurityLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SafeShield_Security_Report.pdf"'
    pdf = canvas.Canvas(response)
    pdf.setTitle("SafeShield Security Report")
    # عنوان التقرير
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, "SafeShield Security Report")
    # معلومات المستخدم
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"User: {request.user.username}")
    pdf.drawString(50, 750, f"Email: {request.user.email}")
    pdf.drawString(50, 730, f"Security Score: {profile.security_score}%")
    # حالة البريد
    email_status = "Verified" if profile.email_verified else "Not Verified"
    pdf.drawString(50, 710, f"Email Status: {email_status}")
    # آخر تسجيل دخول
    if profile.last_login_at:
        pdf.drawString(
            50,
            690,
            f"Last Login: {profile.last_login_at.strftime('%Y-%m-%d %H:%M')}"
        )
    if profile.last_login_ip:
        pdf.drawString(
            50,
            670,
            f"Last Login IP: {profile.last_login_ip}"
        )
    # سجل الأحداث الأمنية
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 630, "Recent Security Events")
    pdf.setFont("Helvetica", 10)
    y = 605
    for log in security_logs:
        event_text = f"{log.created_at.strftime('%Y-%m-%d %H:%M')} - {log.title}"
        pdf.drawString(50, y, event_text)
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 800
    # نهاية التقرير
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        50,
        30,
        "Generated by SafeShield Security Center"
    )
    pdf.save()
    return response
@login_required
def link_scanner(request):
    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        if not url:
            messages.error(
                request,
                _('Please enter a URL to scan.')
            )
            return redirect('accounts:link-scanner')
        # فحص مبدئي للرابط
        suspicious_words = [
            'login-verify',
            'account-verify',
            'free-money',
            'password-reset',
            'secure-login',
        ]
        is_suspicious = any(
            word in url.lower()
            for word in suspicious_words
        )
        if is_suspicious:
            result = 'suspicious'
            messages.warning(
                request,
                _('Warning: This link may be suspicious.')
            )
            SecurityLog.objects.create(
                user=request.user,
                event_type='suspicious_activity',
                title=_('Suspicious link detected'),
                details=f'Potentially suspicious URL scanned: {url}',
                severity='warning',
                source='Link Scanner',
                ip_address=get_client_ip(request),
            )
        else:
            result = 'safe'
            messages.success(
                request,
                _('The link appears to be safe.')
            )
            SecurityLog.objects.create(
                user=request.user,
                event_type='security_scan',
                title=_('Link scan completed'),
                details=f'URL scanned successfully: {url}',
                severity='info',
                source='Link Scanner',
                ip_address=get_client_ip(request),
            )
        return render(
            request,
            'accounts/link_scanner.html',
            {
                'result': result,
                'url': url,
            }
        )
    return render(
        request,
        'accounts/link_scanner.html'
    )