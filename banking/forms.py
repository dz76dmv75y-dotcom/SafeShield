from django import forms


class BankingAccountForm(forms.Form):
    institution = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Bank or service name',
            }
        ),
    )
    account_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Account nickname',
            }
        ),
    )
    account_number = forms.CharField(
        required=False,
        max_length=64,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Last 4 digits or account ID',
            }
        ),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes',
            }
        ),
    )

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number', '').strip()
        return account_number
