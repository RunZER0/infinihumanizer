from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import Humanization
from .sentence_runtime import (
    SentenceTask,
    RewriteRuntime,
    clamp_strength,
    model_temperature,
    plan_document,
    protect_sentence,
    remove_em_dashes,
    reassemble,
    restore_sentence,
    split_sentences,
    transformation_instruction,
    validate_candidate,
)


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
        self.assertContains(response, "Sentence-level rewriting with the meaning kept intact.")
        self.assertContains(response, "300 free today")

    @patch("humanizer.views.rewrite_text", return_value=("A cleaner version.", "qwen/qwen3.7-flash"))
    def test_anonymous_user_can_rewrite_within_daily_limit(self, rewrite):
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "one two three four five",
            "strength": "8",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["saved"])
        self.assertEqual(response.json()["anonymous_remaining"], 295)
        rewrite.assert_called_once_with("one two three four five", strength=8)

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
        self.assertContains(response, "Sentence-level rewriting with the meaning kept intact.")

    @patch("humanizer.views.rewrite_text", return_value=("A cleaner version of the text.", "qwen/qwen3.7-flash"))
    def test_api_rewrites_records_usage_and_saves(self, rewrite):
        self.client.force_login(self.user)
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This is a short source passage with enough words to rewrite clearly.",
            "strength": "8",
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
        rewrite.assert_called_once_with(
            "This is a short source passage with enough words to rewrite clearly.",
            strength=8,
        )

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
            "strength": "7",
        })
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.output_text, "Edited output kept here.")
        self.assertEqual(item.variation, 0.7)

    @override_settings(INFINIAI_ADMIN_EMAIL="valdaceai@gmail.com")
    @patch("humanizer.views.rewrite_text", return_value=("Admin rewrite.", "test-model"))
    def test_admin_has_unlimited_word_balance(self, rewrite):
        admin = User.objects.create_user(
            username="owner",
            email="valdaceai@gmail.com",
            password="strong-password-123",
        )
        admin.profile.word_quota = 0
        admin.profile.words_used = 999999
        admin.profile.is_paid = False
        admin.profile.save()

        self.client.force_login(admin)

        page = self.client.get(reverse("humanizer"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Unlimited")

        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This admin rewrite must work even when the stored word quota is exhausted.",
            "strength": "8",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["word_balance"], "Unlimited")
        rewrite.assert_called_once()

    def test_api_enforces_account_word_balance(self):
        self.user.profile.word_quota = 2
        self.user.profile.words_used = 0
        self.user.profile.is_paid = False
        self.user.profile.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse("humanize_ajax"), {
            "text": "This input is longer than two words.",
            "strength": "8",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("balance", response.json()["error"].lower())


class SentenceRuntimeTests(SimpleTestCase):
    def test_strength_profiles_keep_sampling_temperature_bounded(self):
        self.assertEqual(clamp_strength(0), 1)
        self.assertEqual(clamp_strength(8), 8)
        self.assertEqual(clamp_strength(20), 10)
        self.assertLess(model_temperature(4), model_temperature(8))
        self.assertLessEqual(model_temperature(10), 0.68)

    def test_em_dash_is_removed_at_every_strength(self):
        source = "Layered safeguards—from backup systems to trained operators—reduce risk."
        cleaned = remove_em_dashes(source)
        self.assertNotIn("—", cleaned)
        self.assertEqual(cleaned, "Layered safeguards, from backup systems to trained operators, reduce risk.")

    @override_settings(
        HUMANIZER_BACKEND="openrouter",
        OPENROUTER_API_KEY="test-key",
        HUMANIZER_MAX_CONCURRENCY=6,
    )
    def test_runtime_sends_exactly_one_sentence_per_model_request(self):
        runtime = RewriteRuntime(8)
        tasks = [
            SentenceTask(i, text, text, ())
            for i, text in enumerate([
                "Accountability begins with reasons.",
                "There is also an environmental dimension.",
                "Remote work changes more than location.",
            ])
        ]
        seen = []

        def fake_rewrite(batch, repair=False):
            seen.append([task.id for task in batch])
            task = batch[0]
            return {task.id: task.source + " changed"}, "test-model"

        try:
            with patch.object(runtime, "rewrite_batch", side_effect=fake_rewrite):
                rewritten, _ = runtime.run(tasks)
        finally:
            runtime.close()

        self.assertEqual(sorted(seen), [[0], [1], [2]])
        self.assertEqual(len(rewritten), 3)

    def test_strength8_rejects_unchanged_short_sentence(self):
        valid, reason = validate_candidate(
            "Accountability begins with reasons.",
            "Accountability begins with reasons.",
            8,
        )
        self.assertFalse(valid)
        self.assertEqual(reason, "unchanged")

    def test_strength8_strategy_is_stable_and_uses_lexical_anchors(self):
        source = (
            "Judicial independence is commonly defended as a condition of the rule of law "
            "because courts must decide cases without improper pressure."
        )
        first = transformation_instruction(source, 8)
        second = transformation_instruction(source, 8)
        self.assertEqual(first, second)
        self.assertIn("exact source phrases", first)

    def test_strength8_rejects_colloquial_register_drift(self):
        valid, reason = validate_candidate(
            "Well-planned green space can support physical activity and social contact.",
            "Green spaces can help folks move and meet.",
            8,
        )
        self.assertFalse(valid)
        self.assertEqual(reason, "register-drift")

    def test_strength8_accepts_rough_fragment_like_reconstruction(self):
        valid, reason = validate_candidate(
            "Provenance work is therefore both historical and evidentiary.",
            "Historical and evidentiary, hence the term provenance work.",
            8,
        )
        self.assertTrue(valid)
        self.assertEqual(reason, "ok")

    def test_strength8_rejects_overcompressed_developed_sentence(self):
        valid, reason = validate_candidate(
            "Judicial independence protects courts from improper pressure by government and private interests.",
            "Courts need independence from pressure.",
            8,
        )
        self.assertFalse(valid)
        self.assertEqual(reason, "length")

    def test_sentence_splitter_handles_abbreviations_decimals_and_quotes(self):
        source = 'Dr. Smith recorded 29.5 units. The court called it "a serious problem." Another sentence followed.'
        sentences, separators = split_sentences(source)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "Dr. Smith recorded 29.5 units.")
        self.assertEqual(sentences[1], 'The court called it "a serious problem."')
        self.assertEqual(separators, [" ", " "])

    def test_protected_literals_round_trip_exactly(self):
        source = 'The rate was 29.5% in 2024 (Council of Europe, 2018) and the report called it "material."'
        protected, literals = protect_sentence(source)
        self.assertNotIn("29.5%", protected)
        self.assertNotIn("(Council of Europe, 2018)", protected)
        self.assertEqual(restore_sentence(protected, literals), source)

    def test_formatting_round_trip_preserves_headers_indentation_and_bibliography_exactly(self):
        source = (
            "TITLE\n"
            "Introduction:\n"
            "    First sentence.  Second sentence.\n"
            "\n"
            "References\n"
            "    Smith, J. (2024). Example source.\n"
            "\tDoe, A. (2023). Another source.\n"
        )
        plans, separators, tasks = plan_document(source)
        self.assertEqual([task.source for task in tasks], ["First sentence.", "Second sentence."])

        rewritten = {
            tasks[0].id: "Opening sentence changed.",
            tasks[1].id: "Following sentence changed.",
        }
        output = reassemble(plans, separators, rewritten)
        expected = (
            "TITLE\n"
            "Introduction:\n"
            "    Opening sentence changed.  Following sentence changed.\n"
            "\n"
            "References\n"
            "    Smith, J. (2024). Example source.\n"
            "\tDoe, A. (2023). Another source.\n"
        )
        self.assertEqual(output, expected)

    def test_markdown_works_cited_header_preserves_everything_after_it_verbatim(self):
        source = (
            "Body sentence.\n\n"
            "## Works Cited\n"
            "  Smith, J. Title. Publisher, 2024.\n"
            "    https://example.com/source\n"
        )
        plans, separators, tasks = plan_document(source)
        self.assertEqual([task.source for task in tasks], ["Body sentence."])
        output = reassemble(plans, separators, {tasks[0].id: "Body text changed."})
        self.assertEqual(
            output,
            (
                "Body text changed.\n\n"
                "## Works Cited\n"
                "  Smith, J. Title. Publisher, 2024.\n"
                "    https://example.com/source\n"
            ),
        )

    def test_document_plan_preserves_heading_and_references(self):
        source = "Short Heading\n\nFirst sentence. Second sentence.\n\nReferences\n\nSmith, J. (2024). Example."
        plans, paragraph_separators, tasks = plan_document(source)
        self.assertEqual([task.source for task in tasks], ["First sentence.", "Second sentence."])
        rewritten = {tasks[0].id: "Sentence one changed.", tasks[1].id: "Sentence two changed."}
        output = reassemble(plans, paragraph_separators, rewritten)
        self.assertIn("Short Heading", output)
        self.assertIn("Sentence one changed. Sentence two changed.", output)
        self.assertIn("References", output)
        self.assertIn("Smith, J. (2024). Example.", output)
