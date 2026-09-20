from django.urls import path

from .views import VerifiedEmailLoginView, resend_verification, signup_view

urlpatterns = [
    path("signup/", signup_view, name="account_signup"),
    path("login/", VerifiedEmailLoginView.as_view(), name="account_login"),
    path("resend-verification/", resend_verification, name="resend_verification"),
]
