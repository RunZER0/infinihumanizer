"""
Claude AI Engine (Anthropic)
Uses Claude 3.5 Sonnet for balanced humanization
"""

import os
import anthropic
from anthropic import APITimeoutError
from typing import List, Dict
from humanizer.engine_config import get_engine_config, calculate_temperature


# API Configuration - Read from environment
# Support both ANTHROPIC_API_KEY and CLAUDE_API_KEY for backwards compatibility
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", os.environ.get("CLAUDE_API_KEY", ""))


def humanize_text_claude(text_chunks: List[str]) -> List[str]:
    """
    Humanize text using Claude 3.5 Sonnet.
    
    Args:
        text_chunks: List of text chunks to humanize
        
    Returns:
        List of humanized text chunks
    """
    # Get engine configuration
    config = get_engine_config("claude")
    
    # Initialize Anthropic client with timeout
    # Use 120s timeout to handle large inputs without worker crashes
    # This provides enough time for processing while still failing before
    # the Gunicorn worker timeout (180s)
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        timeout=120.0
    )
    
    humanized_chunks = []
    
    for i, chunk in enumerate(text_chunks):
        # Calculate dynamic temperature for this chunk
        temperature = calculate_temperature(
            config["base_temperature"],
            config["temperature_variation"],
            i
        )
        
        # Format user prompt with the text chunk
        user_prompt = config["user_prompt_template"].format(text=chunk)
        
        try:
            # Make API call to Claude
            message = client.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=temperature,
                system=config["system_prompt"],
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract humanized text
            humanized_text = message.content[0].text
            humanized_chunks.append(humanized_text)
            
        except APITimeoutError as e:
            # Specific handling for Anthropic timeout errors
            raise RuntimeError(f"Claude API timeout after 120 seconds on chunk {i+1}. The request took too long - try reducing input size or try again later.") from e
        except Exception as e:
            # Handle other errors
            error_msg = str(e)
            print(f"Error humanizing chunk {i+1} with Claude: {error_msg}")
            raise RuntimeError(f"Claude API failed on chunk {i+1}: {error_msg}") from e
    
    return humanized_chunks


def test_claude_engine():
    """Test the Claude engine with a sample text."""
    test_text = [
        "The research demonstrates that performance-enhancing drugs have significant health consequences. "
        "Athletes who use these substances face cardiovascular risks and psychological issues."
    ]
    
    print("Testing Claude Engine...")
    print("=" * 80)
    print("Original Text:")
    print(test_text[0])
    print("\n" + "=" * 80)
    
    result = humanize_text_claude(test_text)
    
    print("Humanized Text:")
    print(result[0])
    print("=" * 80)


if __name__ == "__main__":
    test_claude_engine()
