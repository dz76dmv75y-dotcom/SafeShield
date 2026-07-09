import secrets
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    security_score = models.PositiveIntegerField(default=88)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    failed_login_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        if self.locked_until and self.locked_until <= timezone.now():
            self.failed_login_count = 0
            self.locked_until = None
            self.save(update_fields=['failed_login_count', 'locked_until'])
        return False

    def record_failed_login(self):
        self.failed_login_count += 1
        if self.failed_login_count >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['failed_login_count', 'locked_until'])

    def reset_login_tracking(self):
        self.failed_login_count = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_count', 'locked_until'])


class SecurityLog(models.Model):
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('failed_login', 'Failed Login'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('account_created', 'Account Created'),
        ('password_changed', 'Password Changed'),
        ('suspicious_link', 'Suspicious Link'),
        ('application_error', 'Application Error'),
    ]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    title = models.CharField(max_length=150)
    details = models.TextField()
    severity = models.CharField(max_length=20, default='info')
    source = models.CharField(max_length=50, default='System')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} - {self.title}'


class ApplicationErrorLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='error_logs')
    path = models.CharField(max_length=500, blank=True)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message[:80]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, verification_token=secrets.token_urlsafe(24))
    else:
        instance.profile.save()
