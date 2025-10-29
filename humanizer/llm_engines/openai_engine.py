"""
OpenAI Engine for text humanization.
Configuration is managed in engine_config.py for easy editing.
"""

import os
from openai import OpenAI, APITimeoutError
from ..engine_config import get_engine_config, calculate_temperature
from ..multi_stage_pipeline import multi_stage_humanize_gpt4


class OpenAIEngine:
    """OpenAI-based text humanization engine."""
    
    def __init__(self):
        """Initialize OpenAI engine with API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")
        
        # Use 120s timeout to handle large inputs without worker crashes
        # This provides enough time for processing while still failing before
        # the Gunicorn worker timeout (180s)
        self.client = OpenAI(
            api_key=api_key,
            timeout=120.0,
            max_retries=2
        )
        
        # Load configuration from engine_config.py
        self.config = get_engine_config("openai")
    
    def humanize(self, text: str, chunk_index: int = 0) -> str:
        """
        Humanize text using OpenAI with dynamic temperature and streaming.
        
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
            # Use streaming to avoid ReadTimeoutError on large responses
            stream = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                top_p=self.config.get("top_p", 0.9),
                frequency_penalty=self.config.get("frequency_penalty", 0.2),
                presence_penalty=self.config.get("presence_penalty", 0.2),
                max_tokens=self.config["max_tokens"],
                stream=True
            )
            
            # Collect content from stream chunks
            humanized_text = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    humanized_text += chunk.choices[0].delta.content
            
            if not humanized_text:
                raise RuntimeError("OpenAI returned empty response")
            
            return humanized_text.strip()
            
        except APITimeoutError as e:
            # Specific handling for OpenAI timeout errors
            raise RuntimeError(f"OpenAI API timeout after 120 seconds. The request took too long - try reducing input size or try again later.") from e
        except Exception as e:
            # Handle other errors
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e
    
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
            # Use streaming for final review as well to prevent timeouts
            stream = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": "You are a careful text editor who makes only necessary, minimal edits."},
                    {"role": "user", "content": review_prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                top_p=0.8,
                max_tokens=self.config["max_tokens"],
                stream=True
            )
            
            # Collect content from stream chunks
            reviewed_text = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    reviewed_text += chunk.choices[0].delta.content
            
            if not reviewed_text:
                return text  # Return original if review fails
            
            return reviewed_text.strip()
            
        except Exception as e:
            print(f"Warning: OpenAI final review failed: {e}")
            return text  # Return original on error
    
    def humanize_multi_stage(self, text: str) -> str:
        """
        Humanize text using the multi-stage stylistic rewriting pipeline.
        
        This method implements a research-based approach that:
        1. Chunks text by paragraphs (semantic boundaries)
        2. Applies alternating style prompts (Analytical, Reflective, Direct)
        3. Merges chunks back together
        
        Creates non-stationary entropy to evade AI detection.
        Designed for 500-word maximum inputs.
        
        Args:
            text: The text to humanize (max 500 words)
            
        Returns:
            Humanized text with alternating stylistic signatures
        """
        return multi_stage_humanize_gpt4(text, self.client)
