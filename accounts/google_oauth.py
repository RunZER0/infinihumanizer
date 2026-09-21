from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.shortcuts import redirect

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView, OAuth2LoginView


def _callback_url():
    return f"{settings.PUBLIC_BASE_URL}/accounts/google/login/callback/"


class InfiniGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def get_callback_url(self, request, app):
        return _callback_url()


_google_login = OAuth2LoginView.adapter_view(InfiniGoogleOAuth2Adapter)
google_callback = OAuth2CallbackView.adapter_view(InfiniGoogleOAuth2Adapter)


def google_login(request, *args, **kwargs):
    """Start Google OAuth and force the callback to the canonical production origin."""
    if (
        not settings.DEBUG
        and request.get_host().split(":", 1)[0].lower() == "www.byinfini.online"
    ):
        return redirect(
            f"{settings.PUBLIC_BASE_URL}{request.get_full_path()}",
            permanent=True,
        )

    response = _google_login(request, *args, **kwargs)
    location = response.get("Location", "")
    if not location:
        return response

    parsed = urlsplit(location)
    if parsed.netloc.lower() not in {"accounts.google.com", "www.accounts.google.com"}:
        return response

    query = parse_qsl(parsed.query, keep_blank_values=True)
    rewritten = []
    replaced = False
    for key, value in query:
        if key == "redirect_uri":
            rewritten.append((key, _callback_url()))
            replaced = True
        else:
            rewritten.append((key, value))
    if not replaced:
        rewritten.append(("redirect_uri", _callback_url()))

    response["Location"] = urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(rewritten),
            parsed.fragment,
        )
    )
    return response
