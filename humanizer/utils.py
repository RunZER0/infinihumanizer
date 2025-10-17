import os
import re
from openai import OpenAI

# --- Configuration ---
# It's good practice to have configurations at the top.
# Initialize OpenAI client with API key from environment variable.
# Increased timeout and retries for handling larger texts or slow API responses.
try:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        timeout=120.0,  # 2 minutes
        max_retries=3,
    )
except Exception as e:
    print(f"Error: Failed to initialize OpenAI client. Ensure OPENAI_API_KEY is set.")
    print(f"Details: {e}")
    client = None

# --- Helper Function ---

def _trim_to_word_limit(text: str, max_words: int) -> str:
    """
    Trims text to be at or below a specified word count.

    It first performs a hard trim to the word limit, then attempts to
    find the last sentence boundary (., !, ?) within that trimmed text
    to avoid cutting off mid-sentence, provided the result isn't too short.
    """
    if not text:
        return ""

    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    # Perform a hard trim to the word budget first.
    trimmed_text = " ".join(words[:max_words])

    # Find the last sentence-ending punctuation mark.
    # This regex looks for the last occurrence of '.', '!', or '?'
    # followed by a space or the end of the string.
    match = re.search(r'.*[\.!\?](?=\s|$)', trimmed_text)

    if match:
        # If a sentence end is found, trim to that point.
        # We add a check to ensure we don't trim away too much text.
        # For instance, if the only sentence end is very early on.
        candidate = match.group(0).strip()
        if len(candidate.split()) >= max_words * 0.85:  # Don't trim more than 15%
            return candidate

    # If no suitable sentence end is found, return the hard-trimmed text.
    return trimmed_text.strip()

# --- Core Function ---

def humanize_text(text: str):
    """
    Rewrites a given text to sound like a clear but non-native English speaker,
    following a strict set of stylistic rules.

    Args:
        text: The original text to be humanized.

    Returns:
        The rewritten text as a string, or an error message if the API call fails.
    """
    if not client:
        return "Error: OpenAI client is not initialized."

    prepped_text = text.strip()
    if not prepped_text:
        return "Error: Input text cannot be empty."

    input_word_count = len(prepped_text.split())
    # A strict word budget: no more than 20% growth.
    max_words_limit = int(input_word_count * 1.2)

    # Estimate required tokens for the output. A common heuristic is words * 1.33.
    # We add a buffer and set sane limits (e.g., 2000 to 4096 for gpt-4o).
    estimated_tokens = int(max_words_limit * 1.4) + 500  # Safety buffer
    max_tokens_for_completion = max(2000, min(estimated_tokens, 4000))

    # This revised system prompt is more direct, structured, and emphatic.
    # It uses formatting and explicit commands to guide the model's output better.
    system_prompt = f"""
You are an advanced text paraphrasing engine. Your task is to rewrite the user's text to emulate the writing style of a non-native English speaker who is intelligent and clear, but whose writing is not perfectly polished.

You MUST adhere to the following rules without deviation:

**RULE 1: VOCABULARY**
- **Simplify:** Replace at least 50% of complex, ornate, or highly idiomatic words with simpler, more common alternatives.
- **Example:** Instead of "The ubiquitous nature of smartphones has irrevocably altered societal dynamics," write "Everywhere you see smartphones, and this has changed how society works."
- **Preserve Terms:** Do not change essential technical terms, names, or data.

**RULE 2: SENTENCE STRUCTURE (CRITICAL)**
- **High Variation:** You MUST create significant variation in sentence length. The output cannot have uniform sentences. Mix very short sentences (3-5 words), medium sentences (10-15 words), and long sentences (20-30 words) together in a dynamic way.
- **Example of Variation:** "This is a key point. Furthermore, the data shows a clear trend over the last decade, which many researchers have pointed to as evidence. We must consider it. The implications are very big."

**RULE 3: TRANSITIONS AND CONJUNCTIONS**
- **Limited Connectors:** Use transition words like "furthermore," "in addition," "moreover," or "consequently" VERY sparingly. Use a maximum of TWO such words in the entire text.
- **Avoid "And":** Once or twice, replace "and" with one of the formal connectors mentioned above, but never use more than one in a single sentence.

**RULE 4: TONE AND FLOW**
- **Clarity is Key:** The final text must be easy to read and understand. Avoid awkward or nonsensical phrasing.
- **Formal Prose:** Maintain a formal tone suitable for academic or professional writing.
- **No Fragments:** Write in complete sentences. Do not use sentence fragments.
- **Slight Repetition:** The writing should feel slightly repetitive in phrasing, but not to the point of being unnatural or unreadable. This is a subtle effect.

**RULE 5: PUNCTUATION**
- **No Dashes:** DO NOT use em dashes (—) or en dashes (–).
- **Hyphens Only:** Use hyphens (-) only for their standard grammatical purpose (e.g., "well-being," "state-of-the-art"). Do not use them to connect clauses.

**RULE 6: WORD COUNT (ABSOLUTE LIMIT)**
- **Strict Budget:** The final rewritten text MUST NOT exceed **{max_words_limit}** words.
- **Action:** Stop writing immediately when you reach this limit. Do not try to conclude the sentence if it goes over the limit.

**Final Instruction:** Your output must be ONLY the rewritten text. Do not add any commentary, headings, or apologies.
"""

    user_prompt = f"""
Rewrite the following text according to ALL the rules defined in your system instructions.

Original Text:
"{prepped_text}"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.65,      # A balance between creativity and predictability.
            top_p=0.95,            # Allows for some lexical diversity.
            frequency_penalty=0.25, # Slightly discourages repeating the same words.
            presence_penalty=0.15, # Discourages repeating the same topics.
            max_tokens=max_tokens_for_completion
        )

        result_text = response.choices[0].message.content.strip()
        
        # Final safeguard to enforce the word count limit.
        final_output = _trim_to_word_limit(result_text, max_words_limit)

        return final_output

    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return f"Error: Could not process the text due to an API error. Details: {e}"

# --- Example Usage ---
if __name__ == '__main__':
    # Make sure to set your OPENAI_API_KEY environment variable before running.
    # Example: export OPENAI_API_KEY='your-key-here'
    
    sample_text = """
    The proliferation of artificial intelligence represents a paradigm shift in technological evolution,
    fundamentally reshaping industries and societal structures. This transformative potential, however, is
    accompanied by a plethora of multifaceted challenges, including ethical quandaries surrounding autonomous
    decision-making, the socioeconomic ramifications of widespread automation, and the imperative for robust,
    unbiased algorithmic governance. Navigating this complex terrain necessitates a concerted, interdisciplinary
    effort from technologists, policymakers, and ethicists to collaboratively forge a future where AI
    augments human potential equitably and responsibly.
    """

    print("--- Original Text ---")
    print(sample_text.strip())
    print("\n" + "="*50 + "\n")

    humanized_result = humanize_text(sample_text)

    print("--- Humanized Text ---")
    print(humanized_result)
    print(f"\nWord Count: {len(humanized_result.split())}")
