from django.contrib.auth.models import User
from django.db import models


class ThreatAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threat_alerts')
    title = models.CharField(max_length=150)
    summary = models.TextField()
    severity = models.CharField(max_length=20)
    source = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
