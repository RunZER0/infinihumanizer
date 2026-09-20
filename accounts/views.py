import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from allauth.account.models import EmailAddress
from allauth.account.views import LoginView
try:
    from allauth.account.utils import send_email_confirmation
except ImportError:
    # In django-allauth >= 0.50.0, send_email_confirmation may have been moved or removed
    # See: https://github.com/pennersr/django-allauth/blob/main/ChangeLog.rst
    send_email_confirmation = None

from .forms import SignUpForm
from .models import Profile


logger = logging.getLogger(__name__)


class VerifiedEmailLoginView(LoginView):
    def form_valid(self, form):
        from django.conf import settings
        from django.contrib.auth import login

        user = form.user_cache

        # In OFFLINE_MODE or DEBUG, skip email verification entirely
        if getattr(settings, 'OFFLINE_MODE', False) or getattr(settings, 'DEBUG', False):
            self._ensure_profile(user)
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return super().form_valid(form)

        verification_required = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "none") == "mandatory"
        verified = EmailAddress.objects.filter(user=user, verified=True).exists()

        if verification_required and not verified:
            self.request.session['resend_email'] = user.email
            messages.error(
                self.request,
                "⚠️ Your email is not verified. Please check your inbox or resend the link."
            )
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)

        self._ensure_profile(user)
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

    def _ensure_profile(self, user):

        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            logger.info("Created profile for user %s during login", user.pk)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("platformhub:workspace")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save(update_fields=["is_active"])
            Profile.objects.get_or_create(user=user)

            verification_required = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "none") == "mandatory"
            email_address, _ = EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={"primary": True, "verified": not verification_required},
            )

            if verification_required:
                if send_email_confirmation:
                    send_email_confirmation(request, user, email=user.email)
                    messages.success(request, "Check your email to verify the account, then sign in.")
                else:
                    messages.error(request, "Email verification is temporarily unavailable.")
                return redirect("account_login")

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("platformhub:workspace")
        messages.error(request, "Please correct the fields below.")
    else:
        form = SignUpForm()

    return render(request, "account/signup.html", {"form": form})


def resend_verification(request):
    """
    View to resend the verification email if the user logs in but is not verified.
    Triggered only when 'resend_email' is set in session by VerifiedEmailLoginView.
    """
    email = request.session.get('resend_email')
    if email:
        email_address = EmailAddress.objects.filter(email=email).first()
        if email_address and not email_address.verified:
            if send_email_confirmation:
                send_email_confirmation(request, email_address.user, email=email)
                messages.success(request, "✅ A new verification email has been sent.")
            else:
                messages.warning(request, "⚠️ Email verification is not available.")
        else:
            messages.warning(request, "⚠️ This email is already verified or doesn't exist.")
        request.session.pop('resend_email', None)  # Clean up
    else:
        messages.error(request, "❌ Could not resend verification email — no email in session.")
    return redirect(reverse('account_login'))
