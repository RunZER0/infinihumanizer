"""
Test suite for Claude humanizer fixes to ensure:
1. Meta-commentary patterns are properly removed
2. Configuration changes are correctly applied
3. The system handles incomplete responses properly
"""

import re
import unittest
from humanizer.utils import clean_llm_output
from humanizer.engine_config import get_engine_config


class TestClaudeMetaCommentaryRemoval(unittest.TestCase):
    """Test that meta-commentary patterns are properly removed"""
    
    def test_basic_continuation_pattern(self):
        """Test removal of basic '[Continued transformation...' pattern"""
        text = "This is transformed text.\n\n[Continued transformation would follow the same mechanical rules for the remaining text]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("[Continued", cleaned)
        self.assertNotIn("would follow", cleaned)
        self.assertEqual(cleaned, "This is transformed text.")
    
    def test_remaining_text_pattern(self):
        """Test removal of '[The remaining text...' pattern"""
        text = "First part is done.\n[The remaining text would be transformed similarly]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("[The remaining", cleaned)
        self.assertNotIn("would be transformed", cleaned)
    
    def test_ellipsis_pattern(self):
        """Test removal of '...would follow' patterns"""
        text = "Partial transformation here...would follow the same rules for rest"
        cleaned = clean_llm_output(text)
        self.assertNotIn("would follow", cleaned)
    
    def test_multiple_patterns(self):
        """Test removal of multiple meta-commentary patterns"""
        text = """This is the output.
        
[The transformation would continue for the remaining text]
[And so on for the rest]"""
        cleaned = clean_llm_output(text)
        self.assertNotIn("[The transformation", cleaned)
        self.assertNotIn("[And so on", cleaned)
    
    def test_preserves_good_content(self):
        """Test that legitimate content is preserved"""
        text = "This demonstrates the approach. The methodology employs systematic analysis."
        cleaned = clean_llm_output(text)
        self.assertEqual(text.strip(), cleaned)
        self.assertIn("demonstrates", cleaned)
        self.assertIn("methodology", cleaned)
    
    def test_etc_pattern(self):
        """Test removal of [etc.] pattern"""
        text = "First item, second item, third item [etc.]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("[etc.]", cleaned)
        self.assertIn("third item", cleaned)
    
    def test_following_same_pattern(self):
        """Test removal of 'Following the same pattern' meta-commentary"""
        text = "Start of text [Following the same pattern for remaining sections]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("[Following", cleaned)
    
    def test_rest_of_text_pattern(self):
        """Test removal of 'Rest of the text' pattern"""
        text = "Beginning section [Rest of the text would be transformed identically]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("[Rest of", cleaned)


class TestClaudeConfiguration(unittest.TestCase):
    """Test that Claude configuration changes are properly applied"""
    
    def test_model_is_correct(self):
        """Test that Claude model is set correctly"""
        config = get_engine_config("claude")
        self.assertEqual(config["model"], "claude-3-5-sonnet-20241022")
    
    def test_temperature_increased(self):
        """Test that temperature is increased for creative variation"""
        config = get_engine_config("claude")
        self.assertEqual(config["base_temperature"], 0.8)
        self.assertGreater(config["base_temperature"], 0.7)
    
    def test_temperature_variation_increased(self):
        """Test that temperature variation is increased for creative variation"""
        config = get_engine_config("claude")
        self.assertEqual(config["temperature_variation"], 0.15)
        self.assertGreater(config["temperature_variation"], 0.1)
    
    def test_max_tokens_sufficient(self):
        """Test that max_tokens is set high enough for long texts"""
        config = get_engine_config("claude")
        self.assertEqual(config["max_tokens"], 8192)
        self.assertGreaterEqual(config["max_tokens"], 8000)
    
    def test_system_prompt_has_critical_directive(self):
        """Test that system prompt includes CRITICAL directive"""
        config = get_engine_config("claude")
        self.assertIn("CRITICAL", config["system_prompt"])
        self.assertIn("HUMAN ACADEMIC", config["system_prompt"])
    
    def test_system_prompt_promotes_human_writing(self):
        """Test that system prompt promotes human academic writing"""
        config = get_engine_config("claude")
        prompt = config["system_prompt"]
        self.assertIn("NATURAL ENGAGEMENT", prompt)
        self.assertIn("INTERPRETIVE DEPTH", prompt)
        self.assertIn("AUTHENTIC ACADEMIC VOICE", prompt)
    
    def test_user_prompt_emphasizes_natural_writing(self):
        """Test that user prompt emphasizes natural human writing"""
        config = get_engine_config("claude")
        template = config["user_prompt_template"]
        self.assertIn("natural human academic writing", template)
        self.assertIn("engaging, interpretive", template)
        self.assertIn("authentically human", template)
    
    def test_user_prompt_encourages_perspective(self):
        """Test that user prompt encourages analytical perspective"""
        config = get_engine_config("claude")
        template = config["user_prompt_template"]
        self.assertIn("analytical perspective", template)
        self.assertIn("natural flow", template)
        self.assertIn("knowledgeable scholar", template)


class TestCleaningEdgeCases(unittest.TestCase):
    """Test edge cases in meta-commentary removal"""
    
    def test_empty_string(self):
        """Test that empty string is handled"""
        cleaned = clean_llm_output("")
        self.assertEqual(cleaned, "")
    
    def test_whitespace_only(self):
        """Test that whitespace-only string is handled"""
        cleaned = clean_llm_output("   \n\n   ")
        self.assertEqual(cleaned, "")
    
    def test_no_meta_commentary(self):
        """Test that text without meta-commentary is unchanged"""
        text = "This is a normal transformed paragraph with no issues."
        cleaned = clean_llm_output(text)
        self.assertEqual(text, cleaned)
    
    def test_brackets_in_content_preserved(self):
        """Test that legitimate brackets in content are preserved"""
        text = "The study [Smith et al., 2020] demonstrates this approach."
        cleaned = clean_llm_output(text)
        self.assertIn("[Smith et al., 2020]", cleaned)
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive"""
        text = "Text here [CONTINUED TRANSFORMATION WOULD FOLLOW THE SAME RULES]"
        cleaned = clean_llm_output(text)
        self.assertNotIn("CONTINUED", cleaned)


class TestPromptConsistency(unittest.TestCase):
    """Test that prompt changes promote consistency"""
    
    def test_all_engines_have_prompts(self):
        """Test that all engines have valid prompts"""
        for engine in ["claude", "openai", "deepseek"]:
            config = get_engine_config(engine)
            self.assertIn("system_prompt", config)
            self.assertIn("user_prompt_template", config)
            self.assertTrue(len(config["system_prompt"]) > 100)
    
    def test_claude_has_human_writing_focus(self):
        """Test that Claude has focus on natural human academic writing"""
        claude_config = get_engine_config("claude")
        # Claude should emphasize human-like writing
        self.assertIn("CRITICAL", claude_config["system_prompt"])
        self.assertIn("natural", claude_config["user_prompt_template"])


def run_tests():
    """Run all tests and print results"""
    print("=" * 80)
    print("RUNNING CLAUDE HUMANIZER FIX TESTS")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestClaudeMetaCommentaryRemoval))
    suite.addTests(loader.loadTestsFromTestCase(TestClaudeConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestCleaningEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptConsistency))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print()
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print()
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
