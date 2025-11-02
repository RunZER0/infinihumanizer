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
from .models import Profile, WhatsAppVerification
from .whatsapp_verification import (
    generate_verification_code,
    encode_to_morse,
    generate_whatsapp_qr
)
from humanizer.utils import humanize_text_with_engine


logger = logging.getLogger(__name__)


class VerifiedEmailLoginView(LoginView):
    def form_valid(self, form):
        from django.conf import settings
        from django.contrib.auth import login

        # ✅ Debug output to confirm this custom view is active
        print("✅ USING CUSTOM VerifiedEmailLoginView")

        user = form.user_cache
        print(f"   📧 User: {user.username}, Email: {user.email}")

        # In OFFLINE_MODE or DEBUG, skip email verification entirely
        if getattr(settings, 'OFFLINE_MODE', False) or getattr(settings, 'DEBUG', False):
            print("   ⚡ Offline/Debug mode - Skipping email verification")
            self._ensure_profile(user)
            # Explicitly log the user in
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(f"   ✅ User logged in: {self.request.user.is_authenticated}")
            # Just proceed with normal login
            return super().form_valid(form)

        # In production, enforce verification
        verified = EmailAddress.objects.filter(user=user, verified=True).exists()
        print(f"   🔍 Email verified: {verified}")

        if not verified:
            self.request.session['resend_email'] = user.email
            messages.error(
                self.request,
                "⚠️ Your email is not verified. Please check your inbox or resend the link."
            )

            # ✅ Render the login form again with session available immediately
            context = self.get_context_data(form=form)
            return render(self.request, self.template_name, context)

        self._ensure_profile(user)
        # Explicitly log the user in
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"   ✅ User logged in: {self.request.user.is_authenticated}")
        return super().form_valid(form)

    def _ensure_profile(self, user):
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            logger.info("Created profile for user %s during login", user.pk)


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User needs WhatsApp verification
            user.save()
            
            # Create profile for new user
            Profile.objects.get_or_create(user=user)
            
            # Generate verification code and morse encoding
            numeric_code = generate_verification_code()
            encoded_code = encode_to_morse(numeric_code)
            
            # Store verification data
            WhatsAppVerification.objects.create(
                user=user,
                encoded_code=encoded_code,
                numeric_code=numeric_code
            )
            
            # Generate QR code
            qr_code_base64 = generate_whatsapp_qr(user.email, encoded_code)
            
            # Show QR code page
            return render(request, "account/whatsapp_verify.html", {
                "email": user.email,
                "qr_code": qr_code_base64,
                "encoded_code": encoded_code
            })
        else:
            # Form is invalid - log errors for debugging
            logger.error("Signup form validation failed: %s", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, "account/signup.html", {"form": form})


@login_required
def humanizer_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

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


def verify_whatsapp_code(request):
    """
    Endpoint for verifying the 6-digit numeric code sent via WhatsApp.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            verification = WhatsAppVerification.objects.get(user=user)
            
            if verification.is_verified:
                messages.info(request, "This account is already verified.")
                return redirect("account_login")
            
            # Check if submitted code matches
            if code == verification.numeric_code:
                # Activate user
                user.is_active = True
                user.save()
                
                # Mark as verified
                verification.is_verified = True
                from django.utils import timezone
                verification.verified_at = timezone.now()
                verification.save()
                
                # Create verified EmailAddress record for allauth
                EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email,
                    defaults={'verified': True, 'primary': True}
                )
                
                messages.success(request, "✅ Your account has been verified! You can now log in.")
                return redirect("account_login")
            else:
                messages.error(request, "❌ Invalid verification code. Please try again.")
        
        except (User.DoesNotExist, WhatsAppVerification.DoesNotExist):
            messages.error(request, "❌ Email not found or verification pending.")
    
    return render(request, "account/verify_code.html")



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
