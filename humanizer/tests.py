from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Humanization


class HumanizerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="writer",
            email="writer@example.com",
            password="strong-password-123",
        )

    def test_page_is_public(self):
        response = self.client.get(reverse("humanizer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rewrite the text in natural prose.")
        self.assertContains(response, "300 free today")

    @patch("humanizer.views.rewrite_text", return_value=("A cleaner version.", "qwen/qwen3.7-flash"))
    def test_anonymous_user_can_rewrite_within_daily_limit(self, rewrite):
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "one two three four five",
            "temperature": "0.65",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["saved"])
        self.assertEqual(response.json()["anonymous_remaining"], 295)
        rewrite.assert_called_once()

    @override_settings(HUMANIZER_ANON_DAILY_WORDS=5)
    @patch("humanizer.views.rewrite_text", return_value=("A cleaner version.", "qwen/qwen3.7-flash"))
    def test_anonymous_daily_limit_requires_auth_after_use(self, rewrite):
        first = self.client.post(reverse("humanize_ajax"), {"text": "one two three four five"})
        self.assertEqual(first.status_code, 200)
        second = self.client.post(reverse("humanize_ajax"), {"text": "one"})
        self.assertEqual(second.status_code, 429)
        payload = second.json()
        self.assertTrue(payload["limit_reached"])
        self.assertTrue(payload["auth_required"])
        self.assertIn("login_url", payload)
        self.assertIn("signup_url", payload)
        self.assertEqual(rewrite.call_count, 1)

    def test_page_renders_for_signed_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("humanizer"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rewrite the text in natural prose.")

    @patch("humanizer.views.rewrite_text", return_value=("A cleaner version of the text.", "qwen/qwen3.7-flash"))
    def test_api_rewrites_records_usage_and_saves(self, rewrite):
        self.client.force_login(self.user)
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This is a short source passage with enough words to rewrite clearly.",
            "temperature": "0.65",
        })
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertTrue(payload["saved"])
        self.assertEqual(payload["output_text"], "A cleaner version of the text.")
        self.user.profile.refresh_from_db()
        self.assertGreater(self.user.profile.words_used, 0)
        item = Humanization.objects.get(id=payload["humanization_id"])
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.model_name, "qwen/qwen3.7-flash")
        rewrite.assert_called_once()

    def test_signed_in_user_can_save_edited_output(self):
        item = Humanization.objects.create(
            user=self.user,
            source_text="Source",
            output_text="First output",
            input_words=1,
            output_words=2,
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("save_humanization"), {
            "humanization_id": str(item.id),
            "source_text": "Source",
            "output_text": "Edited output kept here.",
            "temperature": "0.7",
        })
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.output_text, "Edited output kept here.")

    def test_api_enforces_account_word_balance(self):
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
