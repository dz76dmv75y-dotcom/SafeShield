from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('security-dashboard/', views.security_dashboard, name='security-dashboard'),
    path('start-security-scan/', views.start_security_scan, name='start-security-scan'),
    path('security-report/', views.security_report, name='security-report'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
   path(
    'download-security-report/',
    views.download_security_report,
    name='download-security-report',
),
    path('verify/<str:token>/', views.verify_email, name='verify-email'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    path(
    'link-scanner/',
    views.link_scanner,
    name='link-scanner'
),

]
import resend
from django.conf import settings
from django.http import HttpResponse


def test_scp_email(request):
    resend.api_key = settings.RESEND_API_KEY

    response = resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": ["safeshield.project@gmail.com"],
        "subject": "SCP - Smart Cyber Protection | Test Email",
        "html": """
        <div style="font-family: Arial, sans-serif; padding: 30px; text-align: center;">
            <h1>🛡️ SCP - Smart Cyber Protection</h1>

            <h2>اختبار نظام البريد الإلكتروني</h2>

            <p>
                هذه رسالة تجريبية من نظام الحماية الذكي SCP.
            </p>

            <p>
                إذا وصلتك هذه الرسالة، فهذا يعني أن نظام البريد يعمل بنجاح.
            </p>

            <hr>

            <p>
                Smart Cyber Protection
            </p>
        </div>
        """,
    })

    return HttpResponse("SCP email test sent successfully!")