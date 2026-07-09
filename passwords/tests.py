from django.test import SimpleTestCase

from .views import analyze_strength


class PasswordStrengthTests(SimpleTestCase):
    def test_weak_password_scores_low(self):
        score = analyze_strength('password')
        self.assertLess(score, 60)

    def test_strong_password_scores_high(self):
        score = analyze_strength('StrongPassword!2026')
        self.assertGreaterEqual(score, 80)
