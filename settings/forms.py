from django import forms

from .models import UserPreference


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['real_time_protection', 'email_notifications', 'dark_mode', 'language', 'security_preferences', 'scan_frequency', 'notification_preferences']
        widgets = {
            'security_preferences': forms.Textarea(attrs={'rows': 3}),
            'notification_preferences': forms.Textarea(attrs={'rows': 3}),
        }
