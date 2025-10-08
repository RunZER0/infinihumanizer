from django.test import TestCase
from unittest.mock import Mock, patch
from humanizer.utils import humanize_text, _wc, SYSTEM_PROMPT, STYLE_DEMO, _build_user_prompt


class HumanizerLogicTests(TestCase):
    """Tests for the improved humanizer logic"""
    
    def test_system_prompt_emphasizes_perplexity(self):
        """Verify that the system prompt emphasizes high perplexity"""
        self.assertIn("high perplexity", SYSTEM_PROMPT.lower())
        self.assertIn("perplexity", SYSTEM_PROMPT.lower())
        
    def test_system_prompt_requires_restructuring(self):
        """Verify that the system prompt requires complete restructuring"""
        self.assertIn("COMPLETELY restructure", SYSTEM_PROMPT)
        self.assertIn("Break apart sentences", SYSTEM_PROMPT)
        
    def test_system_prompt_emphasizes_sentence_variation(self):
        """Verify that the system prompt emphasizes varied sentence lengths"""
        self.assertIn("sentence length", SYSTEM_PROMPT.lower())
        self.assertIn("3-5 word", SYSTEM_PROMPT)
        self.assertIn("25-40 word", SYSTEM_PROMPT)
        
    def test_system_prompt_maintains_formal_tone_requirement(self):
        """Verify that formal tone is still required"""
        self.assertIn("formal", SYSTEM_PROMPT.lower())
        self.assertIn("no slang", SYSTEM_PROMPT.lower())
        
    def test_system_prompt_emphasizes_readability(self):
        """Verify that the system prompt emphasizes readability"""
        self.assertIn("readable", SYSTEM_PROMPT.lower())
        self.assertIn("natural flow", SYSTEM_PROMPT.lower())
        
    def test_style_demo_shows_sentence_variation(self):
        """Verify that the style demo shows varied sentence lengths"""
        # The demo should have both short and long sentences
        humanized_part = STYLE_DEMO.split("Humanized rewrite")[1]
        # Contains short sentences like "Writing has changed."
        self.assertIn("Writing has changed.", humanized_part)
        # Contains longer, complex sentences
        self.assertTrue(any(len(s.split()) > 20 for s in humanized_part.split(".")))
        
    def test_user_prompt_emphasizes_high_perplexity(self):
        """Verify that user prompts emphasize high perplexity"""
        prompt = _build_user_prompt("Test text", 10, 11)
        self.assertIn("HIGH PERPLEXITY", prompt)
        self.assertIn("sophisticated", prompt)
        
    def test_user_prompt_emphasizes_complete_restructuring(self):
        """Verify that user prompts emphasize complete restructuring"""
        prompt = _build_user_prompt("Test text", 10, 11)
        self.assertIn("COMPLETELY restructure", prompt)
        self.assertIn("do not preserve the original sentence order", prompt)
        
    def test_word_count_utility(self):
        """Test word count utility function"""
        self.assertEqual(_wc("This is a test"), 4)
        self.assertEqual(_wc(""), 0)
        self.assertEqual(_wc("One"), 1)
        
    @patch('humanizer.utils._chat_completion_with_retries')
    def test_humanize_text_uses_higher_temperature(self, mock_completion):
        """Verify that humanize_text uses higher temperature for perplexity"""
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {"content": "Test output"}
        mock_completion.return_value = mock_response
        
        # Call the function
        humanize_text("Test input text")
        
        # Verify it was called with higher temperature
        self.assertEqual(mock_completion.call_count, 1)
        call_kwargs = mock_completion.call_args[1]
        
        # Check for increased temperature (should be 0.9)
        self.assertEqual(call_kwargs['temperature'], 0.9)
        
        # Check for increased frequency penalty (should be 0.4)
        self.assertEqual(call_kwargs['frequency_penalty'], 0.4)
        
        # Check for presence penalty (should be 0.3)
        self.assertEqual(call_kwargs['presence_penalty'], 0.3)
        
    @patch('humanizer.utils._chat_completion_with_retries')
    def test_humanize_text_maintains_word_limits(self, mock_completion):
        """Verify that humanize_text respects word count limits"""
        # Mock a response that's too long
        mock_response = Mock()
        mock_response.choices = [Mock()]
        # Create text with 20 words
        long_text = " ".join(["word"] * 20)
        mock_response.choices[0].message = {"content": long_text}
        mock_completion.return_value = mock_response
        
        # Input has 10 words, so ceiling should be 11 (110%)
        result = humanize_text("one two three four five six seven eight nine ten", max_ratio=1.10)
        
        # Result should be trimmed to respect the word limit
        result_word_count = _wc(result)
        self.assertLessEqual(result_word_count, 11)
        
    def test_humanize_text_handles_empty_input(self):
        """Verify that empty input returns empty string"""
        self.assertEqual(humanize_text(""), "")
        self.assertEqual(humanize_text(None), "")
