from django import forms


class ProtectedAccountForm(forms.Form):
    account_type = forms.ChoiceField(choices=[('email', 'Email Account'), ('apple_id', 'Apple ID'), ('icloud', 'iCloud'), ('banking', 'Banking Account'), ('social', 'Social Media')])
    name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=200)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
