from django.urls import path

from .google_oauth import google_callback, google_login
from .views import VerifiedEmailLoginView, resend_verification, signup_view

urlpatterns = [
    path("google/login/", google_login, name="google_login_fixed"),
    path("google/login/callback/", google_callback, name="google_callback"),
    path("signup/", signup_view, name="account_signup"),
    path("login/", VerifiedEmailLoginView.as_view(), name="account_login"),
    path("resend-verification/", resend_verification, name="resend_verification"),
]
