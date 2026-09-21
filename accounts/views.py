import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from allauth.account.models import EmailAddress
from allauth.account.views import LoginView
try:
    from allauth.account.utils import send_email_confirmation
except ImportError:
    send_email_confirmation = None

from .forms import CustomLoginForm, SignUpForm
from .models import Profile
from .verification import session_email_is_verified


logger = logging.getLogger(__name__)


def _safe_next(request, default="platformhub:workspace"):
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        url=target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return target
    return reverse(default)


class VerifiedEmailLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_form"] = SignUpForm()
        context["signup_open"] = self.request.GET.get("signup") == "1"
        return context

    def form_valid(self, form):
        user = form.user_cache

        if getattr(settings, "OFFLINE_MODE", False) or getattr(settings, "DEBUG", False):
            self._ensure_profile(user)
            login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
            return super().form_valid(form)

        verification_required = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "none") == "mandatory"
        verified = EmailAddress.objects.filter(user=user, verified=True).exists()

        if verification_required and not verified:
            self.request.session["resend_email"] = user.email
            messages.error(self.request, "Your email is not verified. Check your inbox or resend the link.")
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)

        self._ensure_profile(user)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return super().form_valid(form)

    def _ensure_profile(self, user):
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            logger.info("Created profile for user %s during login", user.pk)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request))

    next_url = _safe_next(request)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = (form.cleaned_data.get("email") or "").strip().lower()
            if email == getattr(settings, "INFINIAI_ADMIN_EMAIL", "").lower():
                form.add_error("email", "Use Google to create or access the administrator account.")
            else:
                user = form.save()
                user.is_active = True
                user.save(update_fields=["is_active"])
                Profile.objects.get_or_create(user=user)

                verification_required = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "none") == "mandatory"
                already_verified = session_email_is_verified(request, email)
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        "primary": True,
                        "verified": already_verified or not verification_required,
                    },
                )

                if verification_required and not already_verified:
                    if send_email_confirmation:
                        try:
                            send_email_confirmation(request, user, email=user.email)
                            messages.success(request, "Verify your email, then sign in.")
                        except Exception:
                            logger.exception("Could not send signup verification email to %s", user.email)
                            messages.error(request, "We could not send the verification email. Try again shortly.")
                    else:
                        messages.error(request, "Email verification is temporarily unavailable.")
                    login_url = reverse("account_login")
                    return redirect(f"{login_url}?next={next_url}")

                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect(next_url)
        messages.error(request, "Please correct the fields below.")
        return render(request, "account/login.html", {
            "form": CustomLoginForm(request=request),
            "signup_form": form,
            "signup_open": True,
            "redirect_field_name": "next",
            "redirect_field_value": next_url,
        })

    return render(request, "account/login.html", {
        "form": CustomLoginForm(request=request),
        "signup_form": SignUpForm(),
        "signup_open": True,
        "redirect_field_name": "next",
        "redirect_field_value": next_url,
    })


def resend_verification(request):
    email = request.session.get("resend_email")
    if email:
        email_address = EmailAddress.objects.filter(email=email).first()
        if email_address and not email_address.verified:
            if send_email_confirmation:
                try:
                    send_email_confirmation(request, email_address.user, email=email)
                    messages.success(request, "A new verification email has been sent.")
                except Exception:
                    logger.exception("Could not resend verification email to %s", email)
                    messages.error(request, "We could not send another verification email. Try again shortly.")
            else:
                messages.warning(request, "Email verification is not available.")
        else:
            messages.warning(request, "This email is already verified or does not exist.")
        request.session.pop("resend_email", None)
    else:
        messages.error(request, "Could not resend verification email.")
    return redirect(reverse("account_login"))
