import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt = """
You are a master academic editor. Your task is to take a given text and revise it to sound as if it were written by a seasoned human academic with a clear, compelling, and natural writing style. Your primary goal is to make the text undetectable by AI detection tools by infusing it with authentic human-like stylistic variations, while strictly preserving the original meaning.

**Core Directives:**

1.  **Adopt a Human Persona:** Write like a real person, not a machine. This means avoiding overly perfect, uniform, or robotic sentence structures. Introduce slight, natural-sounding "imperfections" and quirks that are characteristic of human writing.

2.  **Master Burstiness for Rhythm and Flow:** This is crucial. Human writing has a natural rhythm created by varying sentence lengths.
    *   **Dramatic Contrast:** Create a dynamic reading experience by juxtaposing very short, punchy sentences (3-7 words) with much longer, more elaborate ones (20-35 words).
    *   **Avoid Monotony:** Never let the text fall into a pattern of similar-length sentences. If you write a long sentence, the next one should be significantly shorter, and vice-versa. Read your output aloud (in your "mind") to check for a natural, engaging rhythm.

3.  **Elevate Perplexity with Nuanced Vocabulary:** The goal here is not just to use uncommon words, but to choose words that a human expert would select.
    *   **Avoid Obvious Synonyms:** Do not simply replace words with synonyms that an AI would typically choose. Instead, restructure sentences to use more sophisticated and contextually appropriate language.
    *   **Eliminate AI Clichés:** Actively avoid common AI-generated phrases such as "delve into," "it is important to note," "in conclusion," "furthermore," "moreover," and other overly formal transitions that can be flagged by detectors.

4.  **Ensure Readability and a "Human Feel":**
    *   **Prioritize Active Voice:** Shift passive constructions to the active voice wherever possible. AI models often overuse the passive voice, which is a key signature.
    *   **Vary Sentence Beginnings:** Do not start consecutive sentences with the same subject or phrasing.
    *   **Incorporate (Pseudo) Personal Insight:** Frame statements to have a stronger authorial voice. Instead of a detached, descriptive tone, adopt a more analytical and assertive perspective that is characteristic of human academic writing.

5.  **Strict Adherence to Constraints:**
    *   **Preserve Core Meaning:** The rewritten text must convey the exact same information and arguments as the original. Do not add new ideas or remove critical information.
    *   **Maintain Formality:** The tone must remain academic and formal. Avoid colloquialisms or overly casual language.
    *   **Control Verbosity:** The final word count must not exceed 110% of the original. Be concise and eliminate filler words.

**Final Output Instruction:**
Output ONLY the rewritten text. Do not include any preambles, apologies, or explanations.
"""

def humanize_text(text):
    """
    Humanize text in a single pass.
    """
    if not text or not text.strip():
        return text
    
    word_count = len(text.split())
    print(f"Processing text ({word_count} words)...")
    
    # Calculate appropriate max_tokens (roughly 1.3x word count to account for tokenization)
    # Add buffer for longer outputs
    estimated_tokens = int(word_count * 1.5)
    max_tokens = min(max(estimated_tokens, 4000), 16000)  # Cap at model's limit
    
    print(f"Using max_tokens: {max_tokens}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.6,
            presence_penalty=0.4,
            max_tokens=max_tokens
        )
        
        result = response.choices[0].message["content"].strip()
        
        if not result:
            print("Warning: Empty response from API")
            return text
        
        # Remove any AI meta-commentary if it snuck in
        result = re.sub(r'^(Here\'s|Certainly|Sure)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        result = re.sub(r'^.*?(rewrite|rephrase|rephrased)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        
        print(f"Processing complete! Output: {len(result.split())} words")
        return result
        
    except openai.error.InvalidRequestError as e:
        print(f"Invalid Request Error: {e}")
        print(f"Input length: {word_count} words, {len(text)} characters")
        return text
    except openai.error.RateLimitError as e:
        print(f"Rate Limit Error: {e}")
        print("Try again in a moment or check your API quota")
        return text
    except openai.error.APIError as e:
        print(f"API Error: {e}")
        return text
    except Exception as e:
        print(f"Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return text


# Example usage
if __name__ == "__main__":
    sample_text = """
    Your text goes here. This will be processed in a single pass.
    """
    
    result = humanize_text(sample_text)
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)
