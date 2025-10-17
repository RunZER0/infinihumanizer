import os
from openai import OpenAI
import re

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def _trim_to_word_limit(text: str, max_words: int) -> str:
    """Trim text to ≤ max_words, preferring to end at a sentence boundary if possible."""
    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    # Hard trim to the word budget first
    trimmed = " ".join(words[:max_words]).strip()

    # Try to backtrack to the last sentence end within the trimmed text
    match = re.search(r"(.+?[\.!\?])(?:\s|$)", trimmed[::-1])
    if match:
        # match is on the reversed string; convert the slice back
        end_at = len(trimmed) - match.start()
        candidate = trimmed[:end_at].strip()
        if len(candidate.split()) >= max_words * 0.8:  # don't over-trim too much
            return candidate

    return trimmed

def humanize_text(text: str):
    # Clean up the input text for processing
    prepped = text.strip()

    # Compute a strict 20% word budget
    max_words = int(len(prepped.split()) * 1.2)

    # Advanced prompt to simulate a specific authorial voice
    system_prompt = """
    You are a paraphrasing system designed to rewrite text in a way that sounds like a non-native English speaker writing clearly but imperfectly. Your output should completely follow the rules given herein:
    1. Use simpler, but clear vocabulary. Half of the time, replace complex or decorative words with basic words.
    2. ensure that snetences are changed dramatically from long to short to very long to very short to medium, avoid uniform sentences at all cost.
    3. Use words like "in addition to", "moreover", "next to", and "furthermore" instead of "and" once or twice in the whole essay, and not more than one in one sentence.
    4. Ensure the sentences are readable and not oddly phrased.
    5. Keep technical terms if they are needed. Avoid too much repetition.
    6. Use hyphens sparingly for related ideas; do not use en dashes (–) or em dashes (—) anywhere.
    7. Avoid elegant transitions but The text should flow smoothly and be readable.
    8. Use full sentences most of the time. Avoid sentence fragments.
    9. Sound slightly repetitive but always natural in the writing.
    10. Do not over-polish. It should feel like a student who writes clearly, but not extravagantly polished.
    11. Always have a different output from the last one you gave.
    12. Always ensure the tone of the writing is formal prose.
    13. Be concise and avoid unnecessary verbose, make sure you DONT add more than  20% extra words on the humanized output.
    """

    user_prompt = f"""
    paraphrase the following text according to the system instructions, adopting them fully in the whole rewrite.

    HARD LIMIT: Keep the rewritten text ≤ {max_words} words. If you reach the limit, stop. Do not add extra commentary.

    Original Text:
    {prepped}
    """

    response = client.chat.completions.create(
        model="gpt-4o",  # Using gpt-4o as the latest available model (gpt-5 when available)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,       # Increased temperature for more creativity
        top_p=0.9,             # Prevents the model from using only the most probable words
        frequency_penalty=0.2, # Slightly penalizes repetitive words
        presence_penalty=0.2,  # Slightly penalizes repetitive concepts
        max_tokens=2000
    )

    # Get the response text and normalize whitespace
    result = response.choices[0].message.content.strip()
    result = re.sub(r"\n{2,}", "\n\n", result)

    # Enforce the ≤ 20% word cap
    result = _trim_to_word_limit(result, max_words)

    return result
