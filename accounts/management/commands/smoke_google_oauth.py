from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import reverse


class Command(BaseCommand):
    help = "Verify Google OAuth uses the registered bare-domain callback from either public host."

    def _callback_from_host(self, host):
        response = Client().get(
            reverse("google_login_fixed"),
            secure=True,
            HTTP_HOST=host,
        )
        if response.status_code not in {301, 302, 303, 307, 308}:
            raise CommandError(
                f"OAuth initiation on {host} did not redirect: {response.status_code}"
            )
        location = response["Location"]
        parsed = urlparse(location)
        if parsed.netloc.lower() != "accounts.google.com":
            raise CommandError(
                f"OAuth initiation on {host} did not go directly to Google: {location}"
            )
        params = parse_qs(parsed.query)
        return (params.get("redirect_uri") or [""])[0]

    def handle(self, *args, **options):
        expected = f"{settings.PUBLIC_BASE_URL}{reverse('google_callback')}"
        callbacks = {
            host: self._callback_from_host(host)
            for host in ("byinfini.online", "www.byinfini.online")
        }
        wrong = {host: value for host, value in callbacks.items() if value != expected}
        if wrong:
            raise CommandError(
                f"Google OAuth redirect_uri mismatch: {wrong!r}, expected {expected!r}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Google OAuth smoke check passed on both hosts: redirect_uri={expected}"
            )
        )
