"""
OpenAI Engine for text humanization.
Configuration is managed in engine_config.py for easy editing.
"""

import os
from openai import OpenAI
from ..engine_config import get_engine_config, calculate_temperature


class OpenAIEngine:
    """OpenAI-based text humanization engine."""
    
    def __init__(self):
        """Initialize OpenAI engine with API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(
            api_key=api_key,
            timeout=25.0,  # Reduced from 90s to fail before worker timeout
            max_retries=1   # Reduced from 2 to fail faster
        )
        
        # Load configuration from engine_config.py
        self.config = get_engine_config("openai")
    
    def humanize(self, text: str, chunk_index: int = 0) -> str:
        """
        Humanize text using OpenAI with dynamic temperature.
        
        Args:
            text: The text to humanize
            chunk_index: Index of chunk for temperature variation
            
        Returns:
            Humanized text from OpenAI
        """
        # Calculate dynamic temperature from config
        temperature = calculate_temperature(
            self.config["base_temperature"],
            self.config["temperature_variation"],
            chunk_index
        )
        
        # Get prompts from config
        system_prompt = self.config["system_prompt"]
        user_prompt = self.config["user_prompt_template"].format(text=text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                top_p=self.config.get("top_p", 0.9),
                frequency_penalty=self.config.get("frequency_penalty", 0.2),
                presence_penalty=self.config.get("presence_penalty", 0.2),
                max_tokens=self.config["max_tokens"]
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("OpenAI returned empty response")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def final_review(self, text: str, chunk_count: int) -> str:
        """
        Final review pass to fix redundancies and smooth transitions.
        
        Args:
            text: The rejoined text to review
            chunk_count: Number of chunks that were processed
            
        Returns:
            Reviewed and polished text
        """
        review_prompt = f"""You are reviewing text that was processed in {chunk_count} chunks and rejoined. Your ONLY task is to fix any redundancies or awkward transitions at chunk boundaries.

CRITICAL RULES:
- DO NOT rewrite the content
- DO NOT change the style or tone
- ONLY fix obvious redundancies (repeated phrases/sentences)
- ONLY smooth awkward transitions between sections
- Make minimal, surgical edits
- If the text flows well, return it unchanged

Text to review:

{text}

Return the text with only necessary fixes applied:"""

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a careful text editor who makes only necessary, minimal edits."},
                    {"role": "user", "content": review_prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                top_p=0.8,
                max_tokens=self.config["max_tokens"]
            )
            
            if not response.choices or not response.choices[0].message.content:
                return text  # Return original if review fails
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Warning: OpenAI final review failed: {e}")
            return text  # Return original on error
