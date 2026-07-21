from django.contrib.auth.models import User
from django.db import models


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    real_time_protection = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=True)
    language = models.CharField(max_length=20, default='en')
    security_preferences = models.TextField(blank=True, default='MFA, phishing monitoring, password health')
    scan_frequency = models.CharField(max_length=20, default='daily')
    notification_preferences = models.TextField(blank=True, default='threats, scans, reports')

    def __str__(self):
        return f'{self.user.username} preferences'

