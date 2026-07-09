from django.test import SimpleTestCase

from .views import analyze_banking_url


class BankingProtectionTests(SimpleTestCase):
    def test_fake_banking_url_is_flagged(self):
        result = analyze_banking_url('https://secure-bank-login.example.com/update')
        self.assertTrue(result['is_suspicious'])
        self.assertEqual(result['risk_level'], 'High')

    def test_legitimate_banking_url_is_marked_safe(self):
        result = analyze_banking_url('https://www.firstbank.com/signin')
        self.assertFalse(result['is_suspicious'])
        self.assertEqual(result['risk_level'], 'Low')
