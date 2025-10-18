from django.test import TestCase
from unittest.mock import MagicMock, patch

from humanizer.utils import SYSTEM_PROMPT, humanize_text


class HumanizerPromptTests(TestCase):
    def test_system_prompt_mentions_key_rules(self):
        self.assertIn("non-native English speaker", SYSTEM_PROMPT)
        self.assertIn("Do not over-polish", SYSTEM_PROMPT)
        self.assertIn("avoid unnecessary verbose", SYSTEM_PROMPT)
        self.assertIn("avoid elegant transitions", SYSTEM_PROMPT)

    @patch("humanizer.utils.client")
    def test_user_prompt_includes_word_limit_and_tone(self, mock_client):
        mock_response = MagicMock()
        mock_response.output_text = "Rewritten text"
        mock_client.responses.create.return_value = mock_response

        humanize_text("This is a sample input text that needs refining.")

        _, kwargs = mock_client.responses.create.call_args
        payload = kwargs["input"]
        system_msg = next(msg for msg in payload if msg["role"] == "system")
        user_msg = next(msg for msg in payload if msg["role"] == "user")

        self.assertEqual(system_msg["content"], SYSTEM_PROMPT)
        self.assertIn("critically analytical stance", user_msg["content"])
        self.assertIn("HARD LIMIT", user_msg["content"])

    @patch("humanizer.utils.client")
    def test_max_output_tokens_is_capped(self, mock_client):
        mock_response = MagicMock()
        mock_response.output_text = "output"
        mock_client.responses.create.return_value = mock_response

        long_input = " ".join(["word"] * 500)
        humanize_text(long_input)

        _, kwargs = mock_client.responses.create.call_args
        self.assertLessEqual(kwargs["max_output_tokens"], 2800)
        self.assertGreaterEqual(kwargs["max_output_tokens"], 1800)
