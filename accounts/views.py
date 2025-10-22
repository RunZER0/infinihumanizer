import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.shortcuts import redirect, render
from django.urls import reverse

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.account.views import LoginView

from .forms import SignUpForm
from .models import Profile
from humanizer.utils import humanize_text_with_engine


logger = logging.getLogger(__name__)


class VerifiedEmailLoginView(LoginView):
    def form_valid(self, form):
        from django.conf import settings

        user = form.user_cache

        # In OFFLINE_MODE or DEBUG, skip email verification entirely
        if getattr(settings, 'OFFLINE_MODE', False) or getattr(settings, 'DEBUG', False):
            if not self._ensure_profile(user):
                context = self.get_context_data(form=form)
                return render(self.request, self.template_name, context)
            return super().form_valid(form)

        # In production, enforce verification
        verified = EmailAddress.objects.filter(user=user, verified=True).exists()

        if not verified:
            self.request.session['resend_email'] = user.email
            messages.error(
                self.request,
                "⚠️ Your email is not verified. Please check your inbox or resend the link."
            )

            # ✅ Render the login form again with session available immediately
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)

        if not self._ensure_profile(user):
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)
        return super().form_valid(form)

    def _ensure_profile(self, user):
        try:
            profile, created = Profile.objects.get_or_create(user=user)
        except DatabaseError as exc:
            logger.exception("Unable to load or create profile for user %s: %s", user.pk, exc)
            messages.error(
                self.request,
                "We couldn't connect to the database to load your account. Please try again in a moment.",
            )
            return False

        if created:
            logger.info("Created profile for user %s during login", user.pk)
        return True


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("humanizer")  # Redirect to the humanizer view
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def humanizer_view(request):
    try:
        profile, _ = Profile.objects.get_or_create(user=request.user)
    except DatabaseError as exc:
        logger.exception("Unable to load profile for user %s: %s", request.user.pk, exc)
        messages.error(
            request,
            "We couldn't connect to the database to load your profile. Please try again shortly.",
        )
        context = {
            "input_text": '',
            "output_text": '',
            "word_count": 0,
            "word_balance": 0,
            "selected_engine": (request.POST.get('engine') or 'claude').lower(),
        }
        return render(request, "humanizer/humanizer.html", context)

    try:
        word_quota = int(getattr(profile, "word_quota", 0) or 0)
        words_used = int(getattr(profile, "words_used", 0) or 0)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Failed to normalize profile word data: %s", exc)
        word_quota = 0
        words_used = 0

    word_balance = max(0, word_quota - words_used)
    input_text = ''
    output_text = ''
    word_count = 0
    selected_engine = (request.POST.get('engine') or 'claude').lower()

    if request.method == "POST":
        input_text = request.POST.get("text", "").strip()
        word_count = len(input_text.split())

        if selected_engine not in ("claude", "openai", "deepseek"):
            messages.error(request, "Invalid engine selection.")
        elif not input_text:
            messages.error(request, "Please provide text to humanize.")
        elif word_count > word_balance:
            messages.error(
                request,
                f"You've exceeded your word balance ({word_balance} words left)."
            )
        else:
            try:
                output_text = humanize_text_with_engine(input_text, selected_engine)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Humanizer request failed: %s", exc)
                messages.error(
                    request,
                    "We couldn't humanize your text right now. "
                    "Please check your API keys and try again.",
                )

    context = {
        "input_text": input_text,
        "output_text": output_text,
        "word_count": word_count,
        "word_balance": word_balance,
        "selected_engine": selected_engine,
    }

    return render(request, "humanizer/humanizer.html", context)


def resend_verification(request):
    """
    View to resend the verification email if the user logs in but is not verified.
    Triggered only when 'resend_email' is set in session by VerifiedEmailLoginView.
    """
    email = request.session.get('resend_email')
    if email:
        email_address = EmailAddress.objects.filter(email=email).first()
        if email_address and not email_address.verified:
            send_email_confirmation(request, email_address.user, email=email)
            messages.success(request, "✅ A new verification email has been sent.")
        else:
            messages.warning(request, "⚠️ This email is already verified or doesn't exist.")
        request.session.pop('resend_email', None)  # Clean up
    else:
        messages.error(request, "❌ Could not resend verification email — no email in session.")
    return redirect(reverse('account_login'))
