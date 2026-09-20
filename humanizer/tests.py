from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HumanizerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="writer",
            email="writer@example.com",
            password="strong-password-123",
        )

    def test_page_requires_login(self):
        response = self.client.get(reverse("humanizer"))
        self.assertEqual(response.status_code, 302)

    def test_page_renders_for_signed_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("humanizer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rewrite the text in natural prose.")

    @patch("humanizer.views.rewrite_text", return_value="A cleaner version of the text.")
    def test_api_rewrites_and_records_usage(self, rewrite):
        self.client.force_login(self.user)
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This is a short source passage with enough words to rewrite clearly.",
            "temperature": "0.65",
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["output_text"], "A cleaner version of the text.")
        self.user.profile.refresh_from_db()
        self.assertGreater(self.user.profile.words_used, 0)
        rewrite.assert_called_once()

    def test_api_enforces_word_balance(self):
        self.user.profile.word_quota = 2
        self.user.profile.words_used = 0
        self.user.profile.is_paid = False
        self.user.profile.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This input is longer than two words.",
            "temperature": "0.65",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("balance", response.json()["error"].lower())
