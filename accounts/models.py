import secrets
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    

    

    email_verified = models.BooleanField(default=False)

    verification_token = models.CharField(
        max_length=64,
        blank=True
    )

    security_score = models.PositiveIntegerField(default=88)

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    company = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    failed_login_count = models.PositiveIntegerField(default=0)

    locked_until = models.DateTimeField(
        null=True,
        blank=True
    )

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    last_login_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ===== OTP =====

    otp_code = models.CharField(
        max_length=128,
        blank=True
    )

    otp_created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    otp_attempts = models.PositiveSmallIntegerField(
        default=0
    )

    otp_last_sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    otp_resend_count = models.PositiveSmallIntegerField(
        default=0
    )

    otp_resend_window_started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    two_factor_enabled = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username

    def is_locked(self):

        if self.locked_until and self.locked_until > timezone.now():
            return True

        if self.locked_until and self.locked_until <= timezone.now():

            self.failed_login_count = 0
            self.locked_until = None

            self.save(
                update_fields=[
                    "failed_login_count",
                    "locked_until",
                ]
            )

        return False

    def record_failed_login(self):

        self.failed_login_count += 1

        if self.failed_login_count >= 5:

            self.locked_until = (
                timezone.now() +
                timedelta(minutes=15)
            )

        self.save(
            update_fields=[
                "failed_login_count",
                "locked_until",
            ]
        )

    def reset_login_tracking(self):

        self.failed_login_count = 0
        self.locked_until = None

        self.save(
            update_fields=[
                "failed_login_count",
                "locked_until",
            ]
        )
    def _clear_otp(self):
        self.otp_code = ""
        self.otp_created_at = None
        self.otp_attempts = 0
        self.save(
            update_fields=[
                "otp_code",
                "otp_created_at",
                "otp_attempts",
            ]
        )

    def _refresh_resend_window(self):
        now = timezone.now()
        if not self.otp_resend_window_started_at:
            self.otp_resend_window_started_at = now
            self.otp_resend_count = 0
        elif now > self.otp_resend_window_started_at + timedelta(hours=1):
            self.otp_resend_window_started_at = now
            self.otp_resend_count = 0

    def can_resend_otp(self):
        now = timezone.now()

        if self.otp_last_sent_at and now < self.otp_last_sent_at + timedelta(seconds=60):
            return False

        self._refresh_resend_window()
        return self.otp_resend_count < 3

    def record_otp_resend(self):
        now = timezone.now()
        self._refresh_resend_window()
        self.otp_resend_count += 1
        self.otp_last_sent_at = now
        self.save(
            update_fields=[
                "otp_resend_count",
                "otp_last_sent_at",
                "otp_resend_window_started_at",
            ]
        )

    def generate_otp(self):
        otp = "".join(secrets.choice("0123456789") for _ in range(6))
        self.otp_code = make_password(otp)
        self.otp_created_at = timezone.now()
        self.otp_attempts = 0
        self.otp_last_sent_at = timezone.now()
        self._refresh_resend_window()

        self.save(
            update_fields=[
                "otp_code",
                "otp_created_at",
                "otp_attempts",
                "otp_last_sent_at",
                "otp_resend_count",
                "otp_resend_window_started_at",
            ]
        )

        return otp

    def verify_otp(self, code):
        if self.otp_attempts >= 5:
            return False, "rate_limit"

        if not self.otp_code or not self.otp_created_at:
            return False, "invalid"

        if timezone.now() > self.otp_created_at + timedelta(minutes=5):
            self._clear_otp()
            return False, "expired"

        if not check_password(code, self.otp_code):
            self.otp_attempts += 1
            self.save(update_fields=["otp_attempts"])
            if self.otp_attempts >= 5:
                return False, "rate_limit"
            return False, "invalid"

        self.email_verified = True
        self.otp_code = ""
        self.otp_created_at = None
        self.otp_attempts = 0

        self.save(
            update_fields=[
                "email_verified",
                "otp_code",
                "otp_created_at",
                "otp_attempts",
            ]
        )

        return True, None

class SecurityLog(models.Model):

    EVENT_TYPES = [
        ("login_success", "Login Success"),
        ("failed_login", "Failed Login"),
        ("suspicious_activity", "Suspicious Activity"),
        ("account_created", "Account Created"),
        ("password_changed", "Password Changed"),
        ("security_scan", "Security Scan"),
        ("suspicious_link", "Suspicious Link"),
        ("application_error", "Application Error"),
    ]

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="security_logs",
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES,
    )

    title = models.CharField(
        max_length=150,
    )

    details = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default="info",
    )

    source = models.CharField(
        max_length=50,
        default="System",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} - {self.title}"
    
class ApplicationErrorLog(models.Model):

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="error_logs",
    )

    path = models.CharField(
        max_length=500,
        blank=True,
    )

    message = models.TextField()

    traceback = models.TextField(
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message[:80]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):

    if created:

        Profile.objects.create(
            user=instance,
            verification_token=secrets.token_urlsafe(24),
        )

    else:

        Profile.objects.get_or_create(
            user=instance,
        )