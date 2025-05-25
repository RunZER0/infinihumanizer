from django.urls import path
from . import views
from .views import VerifiedEmailLoginView, signup_view, resend_verification

urlpatterns = [
    path("signup/", signup_view, name="account_signup"),
    path("login/", VerifiedEmailLoginView.as_view(), name="account_login"),
    path("resend-verification/", resend_verification, name="resend_verification"),  # ✅ Add this
]
