from django.contrib.auth.models import AnonymousUser
from django.core.management.base import BaseCommand, CommandError
from django.test import RequestFactory

from platformhub.catalog import SERVICE_INDEX
from platformhub.views import request_service


class Command(BaseCommand):
    help = "Render every public service request page and fail if any returns an error."

    def handle(self, *args, **options):
        factory = RequestFactory()
        failures = []

        for code in SERVICE_INDEX:
            request = factory.get(f"/request/{code}/")
            request.user = AnonymousUser()
            response = request_service(request, service_code=code)
            if response.status_code != 200:
                failures.append(f"{code}: {response.status_code}")

        if failures:
            raise CommandError("Service request smoke check failed: " + ", ".join(failures))

        self.stdout.write(self.style.SUCCESS(
            f"Service request smoke check passed for {len(SERVICE_INDEX)} services."
        ))
