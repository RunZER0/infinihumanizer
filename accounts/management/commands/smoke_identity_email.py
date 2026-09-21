from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.urls import reverse

from disposable_email import is_disposable

from accounts.models import EmailCodeChallenge


class Command(BaseCommand):
    help = "Verify verified-contact, auth, and HTTPS email wiring."

    def handle(self, *args, **options):
        for name in [
            "account_login",
            "account_signup",
            "account_logout",
            "platformhub:consultation",
            "platformhub:pricing",
        ]:
            reverse(name)

        for template_name in [
            "account/login.html",
            "account/logout.html",
            "platformhub/consultation.html",
            "platformhub/pricing.html",
        ]:
            get_template(template_name)

        if not is_disposable("mailinator.com"):
            raise CommandError("Disposable email blocklist is not active.")

        EmailCodeChallenge.objects.count()

        if not settings.DEBUG and not settings.OFFLINE_MODE:
            if settings.ACCOUNT_EMAIL_VERIFICATION != "mandatory":
                raise CommandError("Production account email verification must be mandatory.")
            if settings.EMAIL_BACKEND != "accounts.email_backend.BrevoAPIEmailBackend":
                raise CommandError("Production email backend must use Brevo HTTPS API.")

        self.stdout.write(
            self.style.SUCCESS(
                "Identity/email smoke check passed: "
                f"verification={settings.ACCOUNT_EMAIL_VERIFICATION} "
                f"brevo_api={'yes' if settings.BREVO_API_KEY else 'no'} "
                f"sender={'yes' if settings.BREVO_SENDER_EMAIL else 'no'}"
            )
        )
