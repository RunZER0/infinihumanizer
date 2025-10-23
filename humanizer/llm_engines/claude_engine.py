"""
Claude AI Engine (Anthropic)
Uses Claude 3.5 Sonnet for balanced humanization
"""

import os
import anthropic
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
    
    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
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
            
        except Exception as e:
            print(f"Error humanizing chunk {i+1} with Claude: {str(e)}")
            raise RuntimeError(f"Claude API failed: {str(e)}") from e
    
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
