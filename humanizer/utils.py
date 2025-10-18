import os
import re
from textwrap import dedent
from openai import OpenAI

# Initialize OpenAI client with API key from environment variable and longer timeout
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=90.0,  # Tighter timeout to prevent long-running calls
    max_retries=2
)

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

SYSTEM_PROMPT = dedent("""
You are a rewriting system designed to simplify text in a way that sounds like a non-native English speaker writing clearly but imperfectly. Your output should be understandable and structured, but slightly awkward or clunky. Follow these rules:
1. Use simpler, clear vocabulary. Half of the time, replace complex or decorative words with basic words.
2. Rewrite long or complex sentences into shorter, easier sentences some of the time. Use wide variety to ensure readability is not affected and longer sentences for better flow occasionally. The alternation between this short-long flow should be very high.
3. Use words like "besides", "as well as", "next to", and "along with" instead of "and" once or twice in the whole essay, and not more than one in one sentence.
4. Ensure the sentences are readable and not oddly phrased.
5. Keep technical terms if they are needed. Avoid too much repetition.
6. Use hyphens sometimes for listing related ideas, but not excessively. Completely avoid using en-dashes.
7. Avoid elegant transitions. The text should flow smoothly and be readable.
8. Use full sentences most of the time. Avoid sentence fragments.
9. Sound slightly repetitive but always natural in the writing.
10. Do not over-polish. It should feel like a student who writes clearly, but not extravagantly polished.
11. Always have a different output from the last one you gave.
12. Always ensure the tone of the writing is formal.
13. Be concise and avoid unnecessary verbose, make sure you DONT add more than 20% extra words on the humanized output.
""")


def humanize_text(text: str):
    # Clean up the input text for processing
    prepped = text.strip()

    # Compute a strict 20% word budget
    input_word_count = len(prepped.split())
    max_words = int(input_word_count * 1.2)
    
    # Calculate required tokens (words * 1.3 for safety + 20% buffer)
    # This ensures we have enough tokens for the output
    estimated_tokens = int(max_words * 1.5) + 500  # Extra buffer for longer texts
    max_tokens = max(1800, min(estimated_tokens, 2800))  # Cap output to keep latency reasonable

    user_prompt = dedent(
        f"""
        Rewrite the following text according to the system instructions, adopting a critically analytical stance.

        HARD LIMIT: Keep the rewritten text ≤ {max_words} words. Stop immediately if you reach the limit.

        Original Text:
        {prepped}
        """
    ).strip()

    try:
        response = client.responses.create(
            model="gpt-5",  # GPT-5 only
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_output_tokens=max_tokens  # Dynamic token limit based on input size
        )

        # Prefer the helper, but fall back to manual reconstruction if needed
        result = (response.output_text or "").strip()

        if not result and getattr(response, "output", None):
            chunks = []
            for item in response.output:
                for content in getattr(item, "content", []) or []:
                    if getattr(content, "type", None) == "output_text":
                        chunks.append(content.text)
            result = "".join(chunks).strip()

        result = re.sub(r"\n{2,}", "\n\n", result)

        # Enforce the ≤ 20% word cap
        result = _trim_to_word_limit(result, max_words)

        return result
    
    except Exception as e:
        # Log the error and return a helpful message
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"OpenAI API error: {str(e)}")
        raise Exception(f"Failed to process text: {str(e)}")
