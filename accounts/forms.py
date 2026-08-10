import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class RegisterForm(forms.Form):

    username = forms.CharField(
        label=_("Username"),
        min_length=3,
        max_length=10,
        help_text=_(
            "3-10 characters. Use English letters, numbers and underscore (_) only."
        ),
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Choose a username",
            }
        ),
    )

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your email",
            }
        ),
    )

    password1 = forms.CharField(
        label=_("Password"),
        help_text=_(
            """
            • At least 8 characters.<br>
            • One uppercase letter.<br>
            • One lowercase letter.<br>
            • One number.<br>
            • One special character.
            """
        ),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "password1",
            }
        ),
    )

    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "id": "password2",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("The two password fields must match.")
            )

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if not re.match(r"^[A-Za-z0-9_]+$", username):
            raise ValidationError(
                _("Only English letters, numbers and underscore (_) are allowed.")
            )

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                _("This username is already in use.")
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _("This email is already registered.")
            )

        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters.")
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain an uppercase letter.")
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain a lowercase letter.")
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("Password must contain a number.")
            )

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            raise ValidationError(
                _("Password must contain a special character.")
            )

        return password

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data["username"].strip(),
            email=self.cleaned_data["email"].lower(),
        )
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _("This email is already registered.")
            )

        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters.")
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain an uppercase letter.")
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain a lowercase letter.")
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("Password must contain a number.")
            )

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            raise ValidationError(
                _("Password must contain a special character.")
            )

        return password


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label=_("Username or Email"),
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Username or Email",
            }
        ),
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self):

        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:

            user = User.objects.filter(
                Q(username__iexact=username) |
                Q(email__iexact=username)
            ).first()

            if user and hasattr(user, "profile"):

                if user.profile.is_locked():
                    raise ValidationError(
                        _(
                            "Your account has been temporarily locked due to repeated failed login attempts."
                        )
                    )

        return super().clean()


class ProfileForm(forms.Form):

    phone = forms.CharField(
        required=False,
        max_length=30,
    )

    company = forms.CharField(
        required=False,
        max_length=100,
    )

    location = forms.CharField(
        required=False,
        max_length=100,
    )


class OTPVerifyForm(forms.Form):

    otp = forms.CharField(
        label=_("Verification Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "placeholder": "______",
                "maxlength": "6",
            }
        ),
    )

    def clean_otp(self):
        otp = self.cleaned_data["otp"].strip()
        if not otp.isdigit():
            raise ValidationError(
                _("Verification code must contain only digits.")
            )
        return otp