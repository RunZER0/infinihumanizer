from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from allauth.account.forms import LoginForm
from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError
from django.conf import settings

# -------------------------------
# SIGN-UP FORM
# -------------------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

# -------------------------------
# CUSTOM LOGIN FORM FOR ALLAUTH
# -------------------------------
class CustomLoginForm(LoginForm):
    def clean(self):
        cleaned_data = super().clean()

        # Authenticate manually to catch the user
        login_value = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')

        user = None
        # If user entered an email (contains '@'), resolve the matching username
        if login_value and '@' in login_value:
            try:
                matched = User.objects.get(email__iexact=login_value.strip())
                user = authenticate(self.request, username=matched.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Fallback: treat as username
            user = authenticate(self.request, username=login_value, password=password)

        self.user_cache = user  # ✅ Important to avoid the attribute error

        if user:
            # In production, enforce verified emails. In offline/local mode, allow login for testing.
            if not (getattr(settings, 'OFFLINE_MODE', False) or getattr(settings, 'DEBUG', False)):
                # Production path (kept for reference):
                # email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
                # if not email_verified:
                #     self.request.session['resend_email'] = user.email
                #     raise ValidationError("⚠️ Your email is not verified. Please verify to continue.")
                email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
                if not email_verified:
                    self.request.session['resend_email'] = user.email
                    raise ValidationError("⚠️ Your email is not verified. Please verify to continue.")
        else:
            raise ValidationError("Invalid login credentials.")

        return cleaned_data

    def get_user(self):
        return self.user_cache
