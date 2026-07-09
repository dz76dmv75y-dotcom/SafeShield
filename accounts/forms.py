from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('Email'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': _('Username'),
            'password1': _('Password'),
            'password2': _('Confirm password'),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username or Email'), max_length=254)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
            if user and getattr(user, 'profile', None) and user.profile.is_locked():
                raise ValidationError(_('This account is temporarily locked after repeated failed sign-in attempts. Please try again later.'))
        return cleaned_data


class ProfileForm(forms.Form):
    phone = forms.CharField(required=False, max_length=30)
    company = forms.CharField(required=False, max_length=100)
    location = forms.CharField(required=False, max_length=100)
