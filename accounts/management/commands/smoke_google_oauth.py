from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse


class Command(BaseCommand):
    help = "Verify Google OAuth always uses the canonical bare-domain callback."

    def handle(self, *args, **options):
        expected_callback = f"{settings.PUBLIC_BASE_URL}{reverse('google_callback')}"

        www = Client().get(
            reverse("google_login_fixed"),
            secure=True,
            HTTP_HOST="www.byinfini.online",
        )
        if www.status_code not in {301, 302, 307, 308}:
            raise CommandError(f"www OAuth route did not redirect: {www.status_code}")
        if www["Location"] != f"{settings.PUBLIC_BASE_URL}{reverse('google_login_fixed')}":
            raise CommandError(f"www OAuth route redirected to unexpected URL: {www['Location']}")

        response = Client().get(
            reverse("google_login_fixed"),
            secure=True,
            HTTP_HOST="byinfini.online",
        )
        if response.status_code not in {301, 302, 303, 307, 308}:
            raise CommandError(f"OAuth initiation did not redirect: {response.status_code}")

        location = response["Location"]
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        callback = (params.get("redirect_uri") or [""])[0]
        if callback != expected_callback:
            raise CommandError(
                f"Google OAuth redirect_uri mismatch: got {callback!r}, expected {expected_callback!r}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Google OAuth smoke check passed: redirect_uri={callback}"
            )
        )
