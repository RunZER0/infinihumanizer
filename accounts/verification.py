import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

from disposable_email import is_disposable

from .models import EmailCodeChallenge


SESSION_VERIFIED_EMAIL = "infini_verified_email"
SESSION_VERIFIED_AT = "infini_verified_email_at"


def normalize_email(value):
    email = (value or "").strip().lower()
    validate_email(email)
    return email


def is_disposable_address(email):
    try:
        return bool(is_disposable(email))
    except Exception:
        return False


def session_email_is_verified(request, email):
    try:
        normalized = normalize_email(email)
    except ValidationError:
        return False
    return request.session.get(SESSION_VERIFIED_EMAIL, "").lower() == normalized


def mark_session_email_verified(request, email):
    normalized = normalize_email(email)
    request.session[SESSION_VERIFIED_EMAIL] = normalized
    request.session[SESSION_VERIFIED_AT] = timezone.now().isoformat()
    if not request.user.is_authenticated:
        request.session.set_expiry(60 * 60 * 24 * 30)
    request.session.modified = True
    return normalized


def issue_email_code(email, name=""):
    normalized = normalize_email(email)
    now = timezone.now()
    challenge, _ = EmailCodeChallenge.objects.get_or_create(email=normalized)

    if challenge.last_sent_at and now - challenge.last_sent_at < timedelta(seconds=60):
        return challenge, False

    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge.code_hash = make_password(code)
    challenge.expires_at = now + timedelta(minutes=10)
    challenge.attempts = 0
    challenge.last_sent_at = now
    challenge.save()

    subject = "Your InfiniAI verification code"
    greeting = f"Hi {name.strip()}," if name and name.strip() else "Hello,"
    text = (
        f"{greeting}\n\n"
        f"Your InfiniAI verification code is {code}.\n"
        "It expires in 10 minutes. If you did not request this code, you can ignore this email."
    )
    html = (
        f"<p>{greeting}</p>"
        "<p>Your InfiniAI verification code is:</p>"
        f"<p style=\"font-size:30px;font-weight:700;letter-spacing:6px\">{code}</p>"
        "<p>It expires in 10 minutes.</p>"
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[normalized],
    )
    message.attach_alternative(html, "text/html")
    message.send(fail_silently=False)
    return challenge, True


def verify_email_code(email, code):
    normalized = normalize_email(email)
    challenge = EmailCodeChallenge.objects.filter(email=normalized).first()
    if not challenge:
        return False, "Request a new code."

    now = timezone.now()
    if not challenge.expires_at or challenge.expires_at <= now:
        return False, "That code has expired. Request a new one."
    if challenge.attempts >= 5:
        return False, "Too many attempts. Request a new code."

    challenge.attempts += 1
    challenge.save(update_fields=["attempts", "updated_at"])

    if not check_password((code or "").strip(), challenge.code_hash):
        return False, "That code is not correct."

    challenge.verified_at = now
    challenge.save(update_fields=["verified_at", "updated_at"])
    return True, ""
