from django import forms


class PasswordEntryForm(forms.Form):
    site = forms.CharField(max_length=150)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    expires_on = forms.DateField(required=False)
