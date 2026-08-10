from django import forms

from .models import ProtectedAccount


class ProtectedAccountForm(forms.Form):
    account_type = forms.ChoiceField(
        choices=ProtectedAccount.ACCOUNT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Example: Personal Instagram'
        })
    )

    username = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '@username or email'
        })
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes'
        })
    )