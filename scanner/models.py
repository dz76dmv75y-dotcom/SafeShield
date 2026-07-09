from django.contrib.auth.models import User
from django.db import models


class ScanHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_history')
    url = models.URLField(max_length=500)
    risk_level = models.CharField(max_length=20)
    is_safe = models.BooleanField(default=True)
    reputation = models.CharField(max_length=20)
    ssl_status = models.CharField(max_length=50)
    reasons = models.TextField(blank=True)
    scan_summary = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.url} ({self.risk_level})'
