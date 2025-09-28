# requirements: openai==0.28.1 (legacy SDK)
# pip install "openai==0.28.1"

import os
import re
import time
import openai

# Read API key from env (same as your old setup)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Preferred/backup models — you can reorder as you like.
DEFAULT_MODELS = ["gpt-5", "gpt-4.1"]

# --- Customize your prompts below (kept from your original) ---
SYSTEM_PROMPT = """
You are an advanced text rewriter that produces naturally human-written content. Your goal is to create text that exhibits genuine human writing patterns while maintaining clarity and academic integrity.

CORE PRINCIPLES:
- Write as if you're a competent human author with natural imperfections
- Vary sentence structure organically without forced patterns
- Use authentic human reasoning flows and idea connections
- Include subtle inconsistencies that occur in natural writing

STRUCTURAL VARIATIONS:
- Mix sentence lengths naturally (some short, some medium, occasional long)
- Vary paragraph lengths based on content complexity
- Use different transition styles: direct statements, questions, examples, contrasts
- Include occasional minor redundancy for emphasis (as humans do)
- Break complex ideas across multiple sentences when natural

VOCABULARY AND TONE:
- Choose words based on context and natural flow, not complexity rules
- Use discipline-appropriate terminology consistently
- Maintain formal tone throughout while allowing natural variation in formality level
- Vary word choice for the same concepts throughout the text
- Use active and passive voice contextually, not systematically

HUMAN WRITING PATTERNS:
- Begin some sentences with conjunctions when it feels natural
- Use parenthetical asides for clarification or examples
- Include rhetorical questions occasionally
- Reference previous points with natural connectors
- Show genuine engagement with the topic through word choice

AUTHENTICITY MARKERS:
- Include subtle personal perspective indicators ("it seems," "appears to be," "suggests")
- Use qualifying language appropriately ("often," "typically," "in many cases")
- Show natural uncertainty where appropriate
- Include context-dependent emphasis through word order
- Maintain consistent but not perfect formatting

FLOW AND COHERENCE:
- Connect ideas through logical association, not formulaic transitions
- Use examples and elaboration naturally within arguments
- Return to key themes without mechanical repetition
- Build arguments progressively with natural development
- Include synthesis and cross-referencing of ideas

Remember: Write as a knowledgeable human would - with purpose, clarity, and natural imperfection. Avoid mechanical patterns or systematic rule application. Focus on authentic communication of ideas.
""".strip()


def humanize_text(
    text: str,
    models: list = None,
    temperature: float = 0.85,
    max_tokens: int = 1600,
    max_retries: int = 3,
    retry_backoff_seconds: float = 2.0,
) -> str:
    """
    Rewrite `text` using legacy ChatCompletion API.
    Tries models in order (e.g., ["gpt-5", "gpt-4.1"]) and falls back if a model fails.
    """

    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")

    if models is None:
        models = DEFAULT_MODELS

    user_prompt = (
        "Rewrite the following text to sound naturally human-written while preserving all "
        "key information, arguments, and academic integrity. Focus on natural flow and authentic "
        "human expression patterns:\n\n" + text
    )

    last_error = None

    for model in models:
        # Simple retry loop per model
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
                )
                result = resp["choices"][0]["message"]["content"].strip()
                # Compress excessive blank lines
                return re.sub(r"\n{2,}", "\n\n", result)

            except openai.error.RateLimitError as e:
                last_error = e
                # Exponential backoff on rate limit
                time.sleep(retry_backoff_seconds * attempt)

            except (openai.error.APIError, openai.error.Timeout, openai.error.APIConnectionError) as e:
                last_error = e
                time.sleep(retry_backoff_seconds * attempt)

            except openai.error.InvalidRequestError as e:
                # Likely bad model id or quota/context issue — break to try next model
                last_error = e
                break

            except Exception as e:
                # Unknown error — break to next model
                last_error = e
                break

        # If we exhausted retries for this model, continue to the next one

    # If we get here, all models/attempts failed
    raise RuntimeError(f"All model attempts failed. Last error: {last_error!r}")


# --- Example usage (optional) ---
if __name__ == "__main__":
    sample = "Paste a paragraph here that you want rewritten in a more natural, human style."
    try:
        print(humanize_text(sample))  # tries gpt-5, then gpt-4.1
    except Exception as exc:
        print(f"Error: {exc}")
