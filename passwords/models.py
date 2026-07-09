import base64
import hashlib
from datetime import date

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class PasswordEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries')
    site = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    encrypted_value = models.TextField()
    notes = models.TextField(blank=True)
    strength_score = models.PositiveIntegerField(default=0)
    expires_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.site

    @staticmethod
    def _get_cipher():
        digest = hashlib.sha256(settings.SECRET_KEY.encode('utf-8')).digest()
        return Fernet(base64.urlsafe_b64encode(digest))

    @classmethod
    def encrypt_password(cls, raw_password):
        return cls._get_cipher().encrypt(raw_password.encode('utf-8')).decode('utf-8')

    @classmethod
    def decrypt_password(cls, encrypted_value):
        return cls._get_cipher().decrypt(encrypted_value.encode('utf-8')).decode('utf-8')

    @property
    def password(self):
        return self.decrypt_password(self.encrypted_value)

    @property
    def health_status(self):
        if self.strength_score >= 85:
            return 'Excellent'
        if self.strength_score >= 65:
            return 'Good'
        return 'Needs attention'

    @property
    def is_expiring(self):
        if not self.expires_on:
            return False
        return (self.expires_on - date.today()).days <= 30
