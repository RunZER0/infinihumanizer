from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Keep browser traffic on the public InfiniAI domain.

    OAuth providers build callback URLs from the current request host. Redirecting
    browser traffic before auth starts guarantees Google sees byinfini.online
    instead of the Render service hostname.
    """

    canonical_host = "byinfini.online"
    aliases = {
        "infiniai.onrender.com",
        "infinihumanizer.onrender.com",
        "www.byinfini.online",
        "infiniaihumanizer.live",
        "www.infiniaihumanizer.live",
    }
    exempt_paths = {"/health/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG or getattr(settings, "OFFLINE_MODE", False):
            return self.get_response(request)

        host = request.get_host().split(":", 1)[0].lower()
        if (
            request.method in {"GET", "HEAD"}
            and host in self.aliases
            and request.path not in self.exempt_paths
        ):
            return HttpResponsePermanentRedirect(
                f"https://{self.canonical_host}{request.get_full_path()}"
            )

        return self.get_response(request)
