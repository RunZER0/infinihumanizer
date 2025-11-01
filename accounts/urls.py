from django.urls import path
from . import views
from .views import VerifiedEmailLoginView, signup_view, resend_verification, verify_whatsapp_code

urlpatterns = [
    path("signup/", signup_view, name="account_signup"),
    path("login/", VerifiedEmailLoginView.as_view(), name="account_login"),
    path("resend-verification/", resend_verification, name="resend_verification"),
    path("verify-whatsapp/", verify_whatsapp_code, name="verify_whatsapp_code"),
]
