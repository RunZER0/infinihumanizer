"""
DeepSeek Engine for text humanization.
Configuration is managed in engine_config.py for easy editing.
"""

import os
import json
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
        Humanize text using DeepSeek with dynamic temperature and streaming.
        
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
            "max_tokens": self.config["max_tokens"],
            "stream": True
        }
        
        try:
            # Use streaming to avoid ReadTimeoutError on large responses
            # Use 120s timeout to handle large inputs without worker crashes
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120, stream=True)
            response.raise_for_status()
            
            # Collect content from SSE stream
            humanized_text = ""
            for line in response.iter_lines():
                if not line:
                    continue
                    
                # Decode line
                line_str = line.decode('utf-8')
                
                # DeepSeek uses SSE format: "data: {json}"
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    
                    # Skip "[DONE]" message
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        # Parse JSON chunk
                        chunk_data = json.loads(data_str)
                        
                        # Extract content delta from chunk
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                humanized_text += content
                    except json.JSONDecodeError:
                        # Skip malformed JSON chunks
                        continue
            
            if not humanized_text:
                raise RuntimeError("DeepSeek returned empty response")
            
            return humanized_text.strip()
            
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"DeepSeek API timeout after 120 seconds. The request took too long - try reducing input size or try again later.") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"DeepSeek API error: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"DeepSeek API response parsing error: {str(e)}") from e
