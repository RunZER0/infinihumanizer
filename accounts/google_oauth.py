from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView, OAuth2LoginView


GOOGLE_CALLBACK_URL = "https://byinfini.online/accounts/google/login/callback/"


class InfiniGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def get_callback_url(self, request, app):
        return GOOGLE_CALLBACK_URL


google_login = OAuth2LoginView.adapter_view(InfiniGoogleOAuth2Adapter)
google_callback = OAuth2CallbackView.adapter_view(InfiniGoogleOAuth2Adapter)
