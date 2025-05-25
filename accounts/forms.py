from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from allauth.account.forms import LoginForm
from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError

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
        user = authenticate(
            self.request,
            username=self.cleaned_data.get('login'),
            password=self.cleaned_data.get('password')
        )

        self.user_cache = user  # ✅ Important to avoid the attribute error

        if user:
            # Check if email is verified
            email_verified = EmailAddress.objects.filter(user=user, verified=True).exists()
            if not email_verified:
                self.request.session['resend_email'] = user.email
                raise ValidationError("⚠️ Your email is not verified. Please verify to continue.")
        else:
            raise ValidationError("Invalid login credentials.")

        return cleaned_data

    def get_user(self):
        return self.user_cache
