"""
Google Gemini Engine for text humanization.
"""

import os
import google.generativeai as genai


class GeminiEngine:
    """Gemini-based text humanization engine."""
    
    def __init__(self):
        """Initialize Gemini engine with API key from environment."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def humanize(self, text: str, chunk_index: int = 0) -> str:
        """
        Humanize text using Gemini with dynamic temperature.
        
        Args:
            text: The text to humanize
            chunk_index: Index of chunk for temperature variation
            
        Returns:
            Humanized text from Gemini
        """
        # Dynamic temperature based on chunk index (0.6 to 0.9)
        temperature = 0.6 + (chunk_index % 4) * 0.1
        
        system_prompt = """You are a text humanizer. Your task is to transform AI-generated text into natural, human-written content.

Guidelines:
- Make the text sound like it was written by a real person
- Vary sentence structure and length naturally
- Use natural transitions and connectors
- Maintain the original meaning and key points
- Remove overly formal or robotic phrasing
- Add subtle human touches without overdoing it
- Keep academic integrity while sounding authentic
- Do NOT add new information or change facts
- Do NOT use overly casual language
- Return ONLY the humanized text, no explanations or meta-commentary"""

        user_prompt = f"Humanize this text while preserving its core message:\n\n{text}"
        
        try:
            # Configure generation parameters
            generation_config = {
                'temperature': temperature,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
            
            # Generate content
            response = self.model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=generation_config
            )
            
            if not response or not response.text:
                raise RuntimeError("Gemini returned empty response")
            
            return response.text.strip()
            
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
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
            generation_config = {
                'temperature': 0.3,  # Lower temperature for consistency
                'top_p': 0.8,
                'max_output_tokens': 2048,
            }
            
            response = self.model.generate_content(
                review_prompt,
                generation_config=generation_config
            )
            
            if not response or not response.text:
                return text  # Return original if review fails
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Warning: Gemini final review failed: {e}")
            return text  # Return original on error
