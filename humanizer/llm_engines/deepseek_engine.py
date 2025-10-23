"""
DeepSeek Engine for text humanization.
Configuration is managed in engine_config.py for easy editing.
"""

import os
import requests
from ..engine_config import get_engine_config, calculate_temperature


class DeepSeekEngine:
    """DeepSeek-based text humanization engine."""
    
    def __init__(self):
        """Initialize DeepSeek engine with API key from environment."""
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY environment variable is not set")
        
        # Load configuration from engine_config.py
        self.config = get_engine_config("deepseek")
        self.model = self.config["model"]
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def humanize(self, text: str, chunk_index: int = 0) -> str:
        """
        Humanize text using DeepSeek with dynamic temperature.
        
        Args:
            text: The text to humanize
            chunk_index: Index of chunk for temperature variation
            
        Returns:
            Humanized text from DeepSeek
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
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": self.config["max_tokens"]
        }
        
        try:
            # Use 90s timeout - Gunicorn is configured for 120s in start.sh
            # This gives DeepSeek time to respond while staying under worker timeout
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            humanized = result['choices'][0]['message']['content'].strip()
            
            return humanized
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"DeepSeek API timeout after 90s - network or API is too slow") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"DeepSeek API error: {str(e)}") from e
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"DeepSeek API response parsing error: {str(e)}") from e
