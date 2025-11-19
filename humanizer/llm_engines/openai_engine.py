"""
Text humanization engine with mode support.
Uses custom-trained model with multiple humanization modes.
"""

import os
import random
import concurrent.futures
from openai import OpenAI, APITimeoutError
from ..modes_config import MODEL_ID, get_mode_config, format_prompt_for_mode, DEFAULT_MODE
from ..multi_stage_pipeline import multi_stage_humanize_gpt4, chunk_text



class TextEngine:
    """Text humanization engine with custom-trained model and modes."""
    
    def __init__(self):
        """Initialize engine with API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("API key not configured")
        
        # Use 120s timeout to handle large inputs without worker crashes
        self.client = OpenAI(
            api_key=api_key,
            timeout=120.0,
            max_retries=2
        )
        
        # Use custom model
        self.model = MODEL_ID
    
    def humanize(self, text: str, mode: str = None) -> str:
        """
        Humanize text using specified mode with intelligent parallel chunking.
        
        Supports up to 3000 words with:
        - Structure preservation (titles, headings, references)
        - Parallel processing for speed
        - Order preservation for coherence
        
        Args:
            text: The text to humanize
            mode: Humanization mode (recommended, readability, formal, conversational, informal, academic)
            
        Returns:
            Humanized text with structure preserved
        """
        # Default to recommended mode
        if not mode:
            mode = DEFAULT_MODE

        # --- PARALLEL CHUNKING LOGIC ---
        # Check word count to decide on chunking
        word_count = len(text.split())
        
        # If text is large (> 350 words), use parallel chunking
        # This allows processing 3000+ words quickly by running chunks in parallel
        if word_count > 350:
            chunks = chunk_text(text)
            
            # Only proceed with parallel processing if we actually have multiple chunks
            if len(chunks) > 1:
                # Helper function for parallel execution
                def process_chunk(index_chunk_tuple):
                    index, chunk = index_chunk_tuple
                    try:
                        # Check if chunk is a title/heading (< 15 words, no period at end)
                        chunk_words = len(chunk.split())
                        is_title = chunk_words < 15 and not chunk.rstrip().endswith('.')
                        
                        # Check if chunk is references (starts with References, Bibliography, etc.)
                        is_reference = any(chunk.strip().lower().startswith(kw) for kw in 
                                         ['references', 'bibliography', 'works cited', 'citations'])
                        
                        # Skip processing for titles and references - return as-is
                        if is_title or is_reference:
                            return index, chunk
                        
                        # Recursive call - will hit the "small text" path below
                        # We pass the same mode to ensure consistency
                        return index, self.humanize(chunk, mode)
                    except Exception:
                        # Return original on error to prevent data loss
                        return index, chunk 
                
                results = []
                # Use ThreadPoolExecutor to run API calls in parallel
                # 5 workers is a good balance for rate limits vs speed
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    # Pass tuples of (index, chunk) to preserve order
                    indexed_chunks = list(enumerate(chunks))
                    futures = [executor.submit(process_chunk, item) for item in indexed_chunks]
                    for future in concurrent.futures.as_completed(futures):
                        results.append(future.result())
                
                # Sort by index to restore original order (CRITICAL for structure)
                results.sort(key=lambda x: x[0])
                
                # Join with double newlines to preserve paragraph structure
                return "\n\n".join([r[1] for r in results])
        # -------------------------------
        
        # Get mode configuration
        mode_config = get_mode_config(mode)


        
        # Prepare prompt based on mode
        if mode_config["use_prompt"]:
            # Mode uses custom prompt
            user_prompt = format_prompt_for_mode(mode, text)
            messages = [
                {"role": "user", "content": user_prompt}
            ]
        else:
            # Recommended mode - no prompt, just the text
            messages = [
                {"role": "user", "content": text}
            ]
        
        # Add random variation to temperature for uniqueness
        # Variation of +/- 0.05 to keep it close to the optimized setting
        base_temp = mode_config["temperature"]
        random_variation = random.uniform(-0.05, 0.05)
        final_temperature = max(0.1, min(1.0, base_temp + random_variation))
        
        try:
            # Use streaming to avoid ReadTimeoutError on large responses
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=final_temperature,
                max_tokens=4000,
                stream=True
            )
            
            # Collect content from stream chunks
            humanized_text = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    humanized_text += chunk.choices[0].delta.content
            
            if not humanized_text:
                raise RuntimeError("Processing returned empty response")
            
            return humanized_text.strip()
            
        except APITimeoutError as e:
            # Specific handling for timeout errors
            raise RuntimeError(f"Request timed out after 120 seconds. The request took too long - try reducing input size or try again later.") from e
        except Exception as e:
            # Handle other errors
            raise RuntimeError(f"Processing error: {str(e)}") from e
    
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
            
        except Exception:
            return text  # Return original on error

    
    def humanize_multi_stage(self, text: str) -> str:
        """
        Humanize text using the multi-stage stylistic rewriting pipeline.
        
        This method implements a research-based approach that:
        1. Chunks text by paragraphs (semantic boundaries)
        2. Applies alternating style prompts (Analytical, Reflective, Direct)
        3. Merges chunks back together
        
        Creates non-stationary entropy to evade AI detection.
        Designed for 1000-word maximum inputs.
        
        Args:
            text: The text to humanize (max 1000 words)
            
        Returns:
            Humanized text with alternating stylistic signatures
        """
        return multi_stage_humanize_gpt4(text, self.client)
