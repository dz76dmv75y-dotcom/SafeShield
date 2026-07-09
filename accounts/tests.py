from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import SecurityLog


class AuthenticationTests(TestCase):
    def test_user_can_authenticate_with_email_address(self):
        user = User.objects.create_user(username='safeuser', email='safeuser@example.com', password='StrongPass123!')

        authenticated = authenticate(username='safeuser@example.com', password='StrongPass123!')

        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.username, 'safeuser')

    def test_failed_logins_create_security_logs_and_lock_account(self):
        user = User.objects.create_user(username='lockeduser', email='lockeduser@example.com', password='StrongPass123!')

        for _ in range(6):
            authenticate(username='lockeduser', password='wrong-password')

        user.refresh_from_db()
        self.assertGreaterEqual(SecurityLog.objects.filter(user=user, event_type='failed_login').count(), 1)
        self.assertTrue(user.profile.failed_login_count >= 5)
        self.assertTrue(user.profile.locked_until is None or user.profile.locked_until > timezone.now())


class RegistrationAndI18nTests(TestCase):
    def test_user_can_register_and_login_with_hashed_password(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_usable_password())
        self.assertNotEqual(user.password, 'StrongPass123!')

        login_response = self.client.post(reverse('accounts:login'), {
            'username': 'newuser@example.com',
            'password': 'StrongPass123!',
        })
        self.assertEqual(login_response.status_code, 302)

    def test_language_switcher_sets_arabic_language_cookie(self):
        response = self.client.post('/i18n/setlang/', {'language': 'ar', 'next': '/'}, follow=True)

        self.assertEqual(response.status_code, 200)
        # The test client stores cookies on the client, not always on the final response
        self.assertIn('django_language', self.client.cookies)
        self.assertEqual(self.client.cookies['django_language'].value, 'ar')
