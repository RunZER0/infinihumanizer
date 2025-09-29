# requirements: openai==0.28.1 (legacy SDK)
# pip install "openai==0.28.1"

import os
import re
import time
import openai

# Read API key from env
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Preferred/backup models
DEFAULT_MODELS = ["gpt-5", "gpt-4.1"]

# --- NEW ANTI-DETECTION PROMPT ---
SYSTEM_PROMPT = """
You are rewriting academic text. Your writing must be indistinguishable from a real student's work.

Write naturally - the way actual students write when they understand the material but aren't trying to impress anyone. Real student writing has:

• Sentences that vary in rhythm - not mechanically alternated, but responding to the complexity of ideas
• Word choices that come from genuine understanding, not thesaurus hunting
• Transitions that emerge from logic, not from a list of "transition words"
• Occasional imperfect phrasings that still communicate clearly
• Natural emphasis patterns - some ideas get more space, others are stated efficiently
• Organic paragraph breaks based on thought completion, not length targets

Your writing voice should reflect someone who:
- Knows the subject matter solidly
- Writes clearly but not perfectly
- Has their own slightly inconsistent style
- Occasionally rephrases things for clarity without realizing it
- Doesn't follow a template

DO NOT:
- Use mechanical sentence length alternation
- Apply systematic vocabulary replacement
- Follow transition formulas
- Create artificial awkwardness
- Write in a detectable pattern

DO:
- Let ideas dictate structure
- Use repetition when natural for emphasis
- Write some dense sections and some lighter ones
- Vary how you introduce and conclude ideas
- Trust your understanding of the content to guide phrasing

The goal isn't to "humanize" artificially - it's to write as a human actually would when thinking through these ideas.
""".strip()


def humanize_text(
    text: str,
    models: list = None,
    temperature: float = 0.7,  # Increased for more variation
    max_tokens: int = 1600,
    max_retries: int = 3,
    retry_backoff_seconds: float = 2.0,
    top_p: float = 0.95,  # Added for better sampling
    frequency_penalty: float = 0.4,  # Discourages repetitive patterns
    presence_penalty: float = 0.2,  # Encourages topic diversity
) -> str:
    """
    Rewrite text with anti-detection parameters.
    """

    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")

    if models is None:
        models = DEFAULT_MODELS

    # Simplified, direct instruction
    user_prompt = (
        "Rewrite this in your own natural academic writing style. Preserve all key arguments "
        "and information, but express them as you would if this were your own work:\n\n" + text
    )

    last_error = None

    for model in models:
        for attempt in range(1, max_retries + 1):
            try:
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                )
                result = resp["choices"][0]["message"]["content"].strip()
                # Compress excessive blank lines
                return re.sub(r"\n{2,}", "\n\n", result)

            except openai.error.RateLimitError as e:
                last_error = e
                time.sleep(retry_backoff_seconds * attempt)

            except (openai.error.APIError, openai.error.Timeout, openai.error.APIConnectionError) as e:
                last_error = e
                time.sleep(retry_backoff_seconds * attempt)

            except openai.error.InvalidRequestError as e:
                last_error = e
                break

            except Exception as e:
                last_error = e
                break

    raise RuntimeError(f"All model attempts failed. Last error: {last_error!r}")


# --- Example usage ---
if __name__ == "__main__":
    sample = "Paste a paragraph here that you want rewritten in a more natural, human style."
    try:
        print(humanize_text(sample))
    except Exception as exc:
        print(f"Error: {exc}")
