from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from accounts.verification import SESSION_VERIFIED_EMAIL


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("account_signup")

    def test_signup_view_uses_unified_auth_screen(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")
        self.assertContains(response, "Create an account")

    def test_login_page_exposes_collapsed_signup(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("account_signup"))
        self.assertContains(response, "Create an account")
        self.assertNotContains(response, '<details class="auth-disclosure auth-signup-disclosure" open>')

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
    def test_signup_creates_user_and_profile_when_verification_not_required(self):
        response = self.client.post(self.signup_url, {
            "email": "testuser@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("platformhub:workspace"), fetch_redirect_response=False)
        user = User.objects.get(email="testuser@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
    def test_signup_with_duplicate_email_username(self):
        User.objects.create_user(username="testuser", email="first@example.com", password="pass123")
        response = self.client.post(self.signup_url, {
            "email": "testuser@different.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(email="testuser@different.com").username, "testuser1")

    def test_signup_with_duplicate_email(self):
        User.objects.create_user(username="existing", email="test@example.com", password="pass123")
        response = self.client.post(self.signup_url, {
            "email": "test@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 200)
        signup_form = response.context["signup_form"]
        self.assertIn("email", signup_form.errors)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
    def test_signup_preserves_safe_next_destination(self):
        response = self.client.post(self.signup_url, {
            "email": "returning@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
            "next": reverse("humanizer"),
        })
        self.assertRedirects(response, reverse("humanizer"), fetch_redirect_response=False)

    def test_admin_email_cannot_be_claimed_with_password_signup(self):
        with self.settings(INFINIAI_ADMIN_EMAIL="valdaceai@gmail.com"):
            response = self.client.post(self.signup_url, {
                "email": "valdaceai@gmail.com",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="valdaceai@gmail.com").exists())
        self.assertContains(response, "Use Google")

    def test_disposable_email_is_rejected(self):
        response = self.client.post(self.signup_url, {
            "email": "someone@mailinator.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="someone@mailinator.com").exists())
        self.assertContains(response, "Use a permanent email address.")

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="InfiniAI <hello@example.com>",
    )
    def test_new_unverified_email_is_forced_through_verification(self):
        response = self.client.post(self.signup_url, {
            "email": "newuser@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(EmailAddress.objects.get(user=user).verified)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_contact_verified_email_skips_second_verification(self):
        session = self.client.session
        session[SESSION_VERIFIED_EMAIL] = "verified@example.com"
        session.save()

        response = self.client.post(self.signup_url, {
            "email": "verified@example.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="verified@example.com")
        self.assertTrue(EmailAddress.objects.get(user=user).verified)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class AdminAccessTests(TestCase):
    def setUp(self):
        self.admin_email = "valdaceai@gmail.com"
        self.user = User.objects.create_user(
            username="owner",
            email=self.admin_email,
            password="strong-password-123",
        )

    def test_matching_email_without_google_identity_is_denied(self):
        self.client.force_login(self.user)
        with self.settings(INFINIAI_ADMIN_EMAIL=self.admin_email):
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 403)

    def test_authorized_google_identity_can_open_admin(self):
        from allauth.socialaccount.models import SocialAccount

        SocialAccount.objects.create(
            user=self.user,
            provider="google",
            uid="google-owner-uid",
            extra_data={"email": self.admin_email},
        )
        self.client.force_login(self.user)
        with self.settings(INFINIAI_ADMIN_EMAIL=self.admin_email):
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)


class BrevoAPIBackendTests(TestCase):
    @patch("accounts.email_backend.requests.post")
    @override_settings(
        BREVO_API_KEY="test-key",
        BREVO_SENDER_EMAIL="hello@example.com",
        BREVO_SENDER_NAME="InfiniAI",
        DEFAULT_FROM_EMAIL="InfiniAI <hello@example.com>",
    )
    def test_backend_uses_https_api(self, post):
        from django.core.mail import EmailMessage
        from accounts.email_backend import BrevoAPIEmailBackend

        post.return_value.raise_for_status.return_value = None
        message = EmailMessage(
            subject="Verification",
            body="Code 123456",
            from_email="InfiniAI <hello@example.com>",
            to=["client@example.com"],
        )
        sent = BrevoAPIEmailBackend().send_messages([message])
        self.assertEqual(sent, 1)
        self.assertEqual(post.call_args.args[0], "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(post.call_args.kwargs["headers"]["api-key"], "test-key")
