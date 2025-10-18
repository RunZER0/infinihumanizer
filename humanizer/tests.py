from django.test import TestCase
from unittest.mock import MagicMock, patch

from humanizer.utils import humanize_text


class HumanizerTests(TestCase):
    @patch("humanizer.utils.client.chat.completions.create")
    def test_humanize_returns_text(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Rewritten text here."
        mock_create.return_value = mock_response

        result = humanize_text("Sample input text")
        self.assertEqual(result, "Rewritten text here.")

    @patch("humanizer.utils.client.chat.completions.create")
    def test_uses_gpt_4o_model(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Output"
        mock_create.return_value = mock_response

        humanize_text("Test input")

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["model"], "gpt-4o")
