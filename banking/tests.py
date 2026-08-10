from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from protection.models import ProtectedAccount


class BankingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='bankuser',
            email='bankuser@example.com',
            password='StrongPass123!'
        )
        self.client = Client()
        self.client.login(username='bankuser', password='StrongPass123!')

    def test_banking_home_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('banking:home'))
        self.assertEqual(response.status_code, 302)

    def test_add_bank_account_creates_protected_account(self):
        response = self.client.post(reverse('banking:home'), {
            'institution': 'Safe Bank',
            'account_name': 'Primary Checking',
            'account_number': '1234',
            'notes': 'Main account for payroll deposits',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProtectedAccount.objects.filter(user=self.user, account_type='banking', name='Primary Checking').exists())
