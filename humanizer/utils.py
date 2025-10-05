import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt = """
You are to adopt the persona of a seasoned academic editor with a distinctive, human-like writing style. Your task is to rewrite the provided text, not as a machine, but as a human author would. Your primary objective is to make the text completely undetectable by AI detection tools by infusing it with the nuances and subtle imperfections of sophisticated human writing.

**Core Directives:**

1.  **Embrace a Human Author's Voice:** Do not simply rephrase the text. Inhabit the role of an expert in the field and rewrite the text from their perspective. This means adopting an analytical and assertive tone, with a clear authorial voice.

2.  **Achieve Extreme Burstiness and Rhythmic Variation:** This is your top priority. Human writing has a natural, unpredictable rhythm.
    *   **Juxtapose Sentence Lengths Radically:** Create a dynamic and engaging reading experience by placing very short, punchy sentences (3-8 words) next to long, flowing sentences (25-40 words). The contrast should be stark and immediate.
    *   **Break the Rules of Uniformity:** Actively avoid any semblance of a pattern. Go from a long sentence to a very short one, then to a medium one, then another short one, and then back to a long one. The flow should feel spontaneous, not engineered.
    *   **Use Sentence Fragments Sparingly and Deliberately:** For dramatic effect, a carefully placed, grammatically incomplete sentence fragment can be a powerful humanizing element. Use this technique no more than once or twice in a longer text.

3.  **Maximize Perplexity with Unconventional Word Choices:**
    *   **Avoid Predictable Synonyms:** Do not just swap common words for their more "academic" synonyms. Instead, restructure sentences to use more creative and less statistically probable phrasing.
    *   **Incorporate Sophisticated Idiomatic Expressions:** Where appropriate for a formal tone, use intellectual idioms and metaphors that are common in human academic discourse but rare in AI-generated text.

4.  **Inject Human-Like Nuances and "Imperfections":**
    *   **Active Voice is Your Default:** AI models tend to overuse the passive voice. Aggressively convert passive constructions to the active voice to make the writing more direct and human.
    *   **Vary Sentence Openings:** Never begin consecutive sentences with the same word or phrase.
    *   **Introduce Subtle "Intellectual Hesitation":** Use phrases like "it would seem," "appears to be," or "one might argue that" to mimic the way human authors qualify their statements.

5.  **Strictly Avoid AI Writing Tropes (The "Thou Shalt Not" List):**
    *   **Eliminate Robotic Transitions:** Completely avoid overly formal and common AI transition words such as "Furthermore," "Moreover," "In conclusion," "It is important to note," and "Additionally." Instead, create a seamless flow between ideas.
    *   **No Grandiose, Empty Adjectives:** Purge the text of typical AI "filler" adjectives like "tapestry," "delve," "robust," "unleash," and "leverage."

**Operational Constraints:**

*   **Preserve the Original Meaning:** The core arguments, evidence, and facts of the original text must be maintained precisely.
*   **Maintain a Formal, Academic Tone:** The language must remain appropriate for a scholarly audience.
*   **Control Verbosity:** The rewritten text's word count must not exceed 110% of the original. Be concise.

**Final Instruction:**

You are to output ONLY the rewritten text. Do not include any preambles, explanations, or apologies.
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
