"""
Tests for streaming implementations in OpenAI and DeepSeek engines.
These tests verify that the streaming functionality works correctly to prevent timeouts.
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()


class TestOpenAIStreaming:
    """Test OpenAI engine streaming implementation"""
    
    @patch('humanizer.llm_engines.openai_engine.OpenAI')
    def test_openai_humanize_with_streaming(self, mock_openai_class):
        """Test that OpenAI engine uses streaming correctly"""
        from humanizer.llm_engines.openai_engine import OpenAIEngine
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create mock stream chunks
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta.content = "This is "
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta.content = "streamed "
        
        mock_chunk3 = Mock()
        mock_chunk3.choices = [Mock()]
        mock_chunk3.choices[0].delta.content = "content."
        
        # Mock stream response
        mock_stream = [mock_chunk1, mock_chunk2, mock_chunk3]
        mock_client.chat.completions.create.return_value = iter(mock_stream)
        
        # Create engine and test
        engine = OpenAIEngine()
        result = engine.humanize("Test text")
        
        # Verify streaming was used
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['stream'] is True, "OpenAI engine should use stream=True"
        
        # Verify content was collected correctly
        assert result == "This is streamed content."
    
    @patch('humanizer.llm_engines.openai_engine.OpenAI')
    def test_openai_final_review_with_streaming(self, mock_openai_class):
        """Test that OpenAI final_review uses streaming correctly"""
        from humanizer.llm_engines.openai_engine import OpenAIEngine
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create mock stream chunks
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta.content = "Reviewed text"
        
        mock_stream = [mock_chunk]
        mock_client.chat.completions.create.return_value = iter(mock_stream)
        
        # Create engine and test
        engine = OpenAIEngine()
        result = engine.final_review("Test text", chunk_count=2)
        
        # Verify streaming was used
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['stream'] is True, "final_review should use stream=True"
        assert result == "Reviewed text"
    
    @patch('humanizer.llm_engines.openai_engine.OpenAI')
    def test_openai_empty_stream_handling(self, mock_openai_class):
        """Test that OpenAI engine handles empty stream correctly"""
        from humanizer.llm_engines.openai_engine import OpenAIEngine
        
        # Mock the OpenAI client with empty stream
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = iter([])
        
        # Create engine and test
        engine = OpenAIEngine()
        
        with pytest.raises(RuntimeError, match="OpenAI returned empty response"):
            engine.humanize("Test text")
    
    @patch('humanizer.llm_engines.openai_engine.OpenAI')
    def test_openai_stream_with_none_content(self, mock_openai_class):
        """Test that OpenAI engine skips chunks with None content"""
        from humanizer.llm_engines.openai_engine import OpenAIEngine
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create mock stream chunks with some None content
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta.content = "Start "
        
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta.content = None  # Should be skipped
        
        mock_chunk3 = Mock()
        mock_chunk3.choices = [Mock()]
        mock_chunk3.choices[0].delta.content = "End"
        
        mock_stream = [mock_chunk1, mock_chunk2, mock_chunk3]
        mock_client.chat.completions.create.return_value = iter(mock_stream)
        
        # Create engine and test
        engine = OpenAIEngine()
        result = engine.humanize("Test text")
        
        # Verify only non-None content was collected
        assert result == "Start End"


class TestDeepSeekStreaming:
    """Test DeepSeek engine streaming implementation"""
    
    @patch('humanizer.llm_engines.deepseek_engine.requests.post')
    def test_deepseek_humanize_with_streaming(self, mock_post):
        """Test that DeepSeek engine uses streaming correctly"""
        from humanizer.llm_engines.deepseek_engine import DeepSeekEngine
        
        # Mock SSE stream response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        # Create SSE formatted data
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"This is "}}]}',
            b'data: {"choices":[{"delta":{"content":"streamed "}}]}',
            b'data: {"choices":[{"delta":{"content":"content."}}]}',
            b'data: [DONE]',
        ]
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_post.return_value = mock_response
        
        # Create engine and test (mock the API key)
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        engine = DeepSeekEngine()
        result = engine.humanize("Test text")
        
        # Verify streaming was used
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['stream'] is True, "DeepSeek engine should use stream=True"
        assert 'stream' in call_kwargs['json'], "Payload should include stream parameter"
        assert call_kwargs['json']['stream'] is True
        
        # Verify content was collected correctly
        assert result == "This is streamed content."
    
    @patch('humanizer.llm_engines.deepseek_engine.requests.post')
    def test_deepseek_sse_parsing(self, mock_post):
        """Test that DeepSeek engine correctly parses SSE format"""
        from humanizer.llm_engines.deepseek_engine import DeepSeekEngine
        
        # Mock SSE stream response with various edge cases
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        sse_lines = [
            b'',  # Empty line - should be skipped
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'',  # Another empty line
            b'data: {"choices":[{"delta":{"content":" World"}}]}',
            b'not-data-line',  # Invalid line - should be skipped
            b'data: [DONE]',  # End marker
        ]
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_post.return_value = mock_response
        
        # Create engine and test
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        engine = DeepSeekEngine()
        result = engine.humanize("Test text")
        
        # Verify correct parsing
        assert result == "Hello World"
    
    @patch('humanizer.llm_engines.deepseek_engine.requests.post')
    def test_deepseek_empty_stream_handling(self, mock_post):
        """Test that DeepSeek engine handles empty stream correctly"""
        from humanizer.llm_engines.deepseek_engine import DeepSeekEngine
        
        # Mock empty stream response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter([b'data: [DONE]'])
        mock_post.return_value = mock_response
        
        # Create engine and test
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        engine = DeepSeekEngine()
        
        with pytest.raises(RuntimeError, match="DeepSeek returned empty response"):
            engine.humanize("Test text")
    
    @patch('humanizer.llm_engines.deepseek_engine.requests.post')
    def test_deepseek_malformed_json_handling(self, mock_post):
        """Test that DeepSeek engine handles malformed JSON gracefully"""
        from humanizer.llm_engines.deepseek_engine import DeepSeekEngine
        
        # Mock stream with malformed JSON
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Good "}}]}',
            b'data: {malformed json}',  # Should be skipped
            b'data: {"choices":[{"delta":{"content":"content"}}]}',
            b'data: [DONE]',
        ]
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_post.return_value = mock_response
        
        # Create engine and test
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        engine = DeepSeekEngine()
        result = engine.humanize("Test text")
        
        # Should skip malformed JSON and continue
        assert result == "Good content"
    
    @patch('humanizer.llm_engines.deepseek_engine.requests.post')
    def test_deepseek_delta_without_content(self, mock_post):
        """Test that DeepSeek engine handles deltas without content"""
        from humanizer.llm_engines.deepseek_engine import DeepSeekEngine
        
        # Mock stream with deltas that don't have content
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        sse_lines = [
            b'data: {"choices":[{"delta":{"role":"assistant"}}]}',  # No content
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{}}]}',  # Empty delta
            b'data: {"choices":[{"delta":{"content":" World"}}]}',
            b'data: [DONE]',
        ]
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_post.return_value = mock_response
        
        # Create engine and test
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        engine = DeepSeekEngine()
        result = engine.humanize("Test text")
        
        # Should only collect actual content
        assert result == "Hello World"


class TestClaudeMaxTokens:
    """Test Claude engine max_tokens configuration and stop_reason handling"""
    
    @patch('humanizer.llm_engines.claude_engine.anthropic.Anthropic')
    def test_claude_max_tokens_configuration(self, mock_anthropic_class):
        """Test that Claude engine uses increased max_tokens"""
        from humanizer.llm_engines.claude_engine import humanize_text_claude
        
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Create mock message response
        mock_message = Mock()
        mock_message.content = [Mock(text="Humanized text")]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message
        
        # Set API key
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Call function
        result = humanize_text_claude(["Test text"])
        
        # Verify max_tokens is set to 8192
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['max_tokens'] == 8192, "Claude should use max_tokens=8192"
        
        # Verify result
        assert len(result) == 1
        assert result[0] == "Humanized text"
    
    @patch('humanizer.llm_engines.claude_engine.anthropic.Anthropic')
    def test_claude_stop_reason_max_tokens(self, mock_anthropic_class):
        """Test that Claude engine detects and warns about max_tokens truncation"""
        from humanizer.llm_engines.claude_engine import humanize_text_claude
        
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Create mock message response with max_tokens stop reason
        mock_message = Mock()
        mock_message.content = [Mock(text="Truncated text")]
        mock_message.stop_reason = "max_tokens"
        mock_client.messages.create.return_value = mock_message
        
        # Set API key
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Call function
        result = humanize_text_claude(["Test text"])
        
        # Verify warning was appended
        assert len(result) == 1
        assert "Warning: Output may be incomplete" in result[0]
        assert "Truncated text" in result[0]
    
    @patch('humanizer.llm_engines.claude_engine.anthropic.Anthropic')
    def test_claude_stop_reason_end_turn(self, mock_anthropic_class):
        """Test that Claude engine doesn't add warning for normal completion"""
        from humanizer.llm_engines.claude_engine import humanize_text_claude
        
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # Create mock message response with normal stop reason
        mock_message = Mock()
        mock_message.content = [Mock(text="Complete text")]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message
        
        # Set API key
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        # Call function
        result = humanize_text_claude(["Test text"])
        
        # Verify no warning was added
        assert len(result) == 1
        assert result[0] == "Complete text"
        assert "Warning" not in result[0]


class TestErrorHandling:
    """Test improved error handling in views.py"""
    
    def test_text_length_validation_error(self):
        """Test that text length validation returns proper HTTP 413"""
        from humanizer.utils import humanize_text_with_engine
        
        # Create text that's too long
        too_long_text = "a" * 15000  # Exceeds MAX_TOTAL_CHARS (10000)
        
        with pytest.raises(ValueError, match="Text too long"):
            humanize_text_with_engine(too_long_text, "claude")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
