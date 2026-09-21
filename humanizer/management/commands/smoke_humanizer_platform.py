from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.urls import reverse

from humanizer.models import (
    AnonymousHumanizerUsage,
    ClientConversation,
    ClientMessage,
    Humanization,
)
from platformhub.catalog import PACKAGES


class Command(BaseCommand):
    help = "Verify Humanizer, workspace chat, and tool-entitlement wiring."

    def handle(self, *args, **options):
        expected_credits = {
            "humanizer-individual": 100000,
            "humanizer-pro": 250000,
            "humanizer-team": 600000,
        }
        for slug, credits in expected_credits.items():
            package = PACKAGES.get(slug)
            if not package or int(package.get("word_credits") or 0) != credits:
                raise CommandError(f"Package entitlement mismatch: {slug}")

        if int(settings.HUMANIZER_ANON_DAILY_WORDS) != 300:
            raise CommandError("Anonymous Humanizer daily limit must be 300 words.")

        for name in [
            "humanizer",
            "humanize_ajax",
            "save_humanization",
            "platformhub:workspace",
            "platformhub:client_chat",
            "platformhub:start_checkout",
            "platformhub:verify_checkout",
        ]:
            reverse(name)

        for template_name in [
            "humanizer/humanizer.html",
            "platformhub/workspace.html",
            "platformhub/client_chat.html",
            "platformhub/checkout.html",
        ]:
            get_template(template_name)

        # Touch the new tables so deployment fails before serving if a migration is missing.
        Humanization.objects.count()
        AnonymousHumanizerUsage.objects.count()
        ClientConversation.objects.count()
        ClientMessage.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                "Humanizer/platform smoke check passed: "
                f"openrouter={'yes' if settings.OPENROUTER_API_KEY else 'no'} "
                f"model={settings.HUMANIZER_MODEL_ID} "
                f"anon_daily={settings.HUMANIZER_ANON_DAILY_WORDS}"
            )
        )
