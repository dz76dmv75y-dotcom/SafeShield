from django.test import SimpleTestCase

from .views import analyze_url


class ScannerAnalysisTests(SimpleTestCase):
    def test_suspicious_url_is_flagged(self):
        result = analyze_url('https://secure-paypal-login.example.com')
        self.assertFalse(result['is_safe'])
        self.assertEqual(result['risk_level'], 'Critical')

    def test_safe_url_is_marked_safe(self):
        result = analyze_url('https://example.com')
        self.assertTrue(result['is_safe'])
        self.assertEqual(result['risk_level'], 'Low')

    def test_phishing_like_url_is_marked_high_risk(self):
        result = analyze_url('http://banking-update-login.example')
        self.assertFalse(result['is_safe'])
        self.assertIn('High', result['risk_level'])
