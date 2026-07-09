from django.contrib.auth.models import User
from django.db import models


class ProtectedAccount(models.Model):
    ACCOUNT_TYPES = [
        ('email', 'Email Account'),
        ('apple_id', 'Apple ID'),
        ('icloud', 'iCloud'),
        ('banking', 'Banking Account'),
        ('social', 'Social Media'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='protected_accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='Protected')
    security_recommendation = models.TextField(blank=True)
    last_checked = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.account_type})'


class SecurityEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_events')
    event_type = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    details = models.TextField()
    severity = models.CharField(max_length=20, default='info')
    source = models.CharField(max_length=50, default='System')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
