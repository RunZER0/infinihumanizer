# humanize.py
import os
import re
import math
import time
import random

# --- Optional: if you're on the legacy SDK this import exists.
#     If you later upgrade, this still works; we only use ChatCompletion.
import openai

# Ensure the API key is set
if not os.environ.get("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set in environment.")

openai.api_key = os.environ["OPENAI_API_KEY"]

# -----------------------------
# Utilities
# -----------------------------
_WORD_RE = re.compile(r"\b\w+\b")

def _wc(s: str) -> int:
    return len(_WORD_RE.findall(s))

def _trim_to_cap(text: str, cap_words: int) -> str:
    words = text.split()
    if len(words) <= cap_words:
        return text.strip()
    cut = " ".join(words[:cap_words]).strip()
    # try ending at a sentence boundary
    last_period = cut.rfind(".")
    if last_period > 0:
        return cut[:last_period+1].strip()
    return cut

def _clean_paragraphs(text: str) -> str:
    # collapse excessive blank lines
    out = re.sub(r"\n{3,}", "\n\n", text.strip())
    return out

# -----------------------------
# Prompts (compatible with old SDK)
# -----------------------------
SYSTEM_PROMPT = (
    "You are an expert at transforming AI-generated text into authentic human writing.\n\n"
    "Core Principles:\n"
    "- Human writing is highly readable with natural flow and rhythm.\n"
    "- Real humans use diverse vocabulary and complex sentence structures (high perplexity).\n"
    "- Sentence lengths vary dramatically - short punchy statements mixed with longer, nuanced explanations.\n"
    "- Humans restructure ideas completely, not just swap words sentence-by-sentence.\n"
    "- Natural writing includes subtle transitions, occasional emphasis through repetition, and thoughtful pacing.\n\n"
    "Your Task:\n"
    "- COMPLETELY restructure the content. Break apart sentences, recombine ideas, reorder concepts.\n"
    "- Vary sentence length extensively: use 3-5 word sentences alongside 25-40 word complex sentences.\n"
    "- Use sophisticated vocabulary and varied phrasing to increase perplexity.\n"
    "- Create natural reading flow - the text should feel effortless to read despite complexity.\n"
    "- Maintain formal academic tone throughout (no slang, contractions, or casual language).\n"
    "- Preserve all facts, quotes, citations, numbers, and technical terms exactly.\n"
    "- Avoid robotic transition phrases: furthermore, moreover, in addition, it is important to note, additionally, consequently.\n"
    "- Respect the word count limits provided.\n\n"
    "Output only the rewritten text. No prefaces, explanations, or metadata."
)

STYLE_DEMO = (
    "Source (excerpt):\n"
    "AI systems significantly influence writing workflows. It is important to note that authors should adapt. "
    "Furthermore, these technologies reshape academic practices. Moreover, proper training ensures effectiveness.\n\n"
    "Humanized rewrite (style to imitate):\n"
    "Writing has changed. AI systems now permeate every stage of the composition process, from initial drafting "
    "through final revision. This transformation demands adaptation from authors, yet panic serves no purpose. "
    "What scholars require instead are practical methodologies for engaging these tools effectively. Academic practices "
    "evolve continuously, and this technological shift represents merely another phase in that ongoing development. "
    "Training becomes paramount—not superficial familiarity, but deep understanding of how these systems operate, "
    "where they excel, and crucially, where human judgment remains irreplaceable."
)

def _build_user_prompt(src: str, original_words: int, ceiling_words: int) -> str:
    return (
        f"ORIGINAL_WORDS={original_words}\n"
        f"CEILING_WORDS={ceiling_words}\n\n"
        "Transform the text below into authentic human writing with these requirements:\n"
        "1. COMPLETELY restructure - do not preserve the original sentence order or structure\n"
        "2. Create HIGH PERPLEXITY - use sophisticated, varied vocabulary and complex sentence constructions\n"
        "3. Vary sentence length dramatically (from very short to very long)\n"
        "4. Ensure excellent readability despite complexity\n"
        "5. Maintain strict formal academic tone\n"
        "6. Stay within the word count limit\n\n"
        "Output only the transformed text:\n\n"
        f"{src.strip()}"
    )

# -----------------------------
# Robust legacy call with retries
# -----------------------------
# We’ll try models in order and degrade if unsupported on your SDK.
MODEL_CANDIDATES = [
    # Try GPT-4.1 if available to your account on Chat Completions:
    "gpt-4.1",
    # Some Render setups only have 4o/mini models available:
    "gpt-4o",
    "gpt-4o-mini",
    # Only attempt gpt-5 if your legacy SDK/model gateway actually supports it.
    # (Most old ChatCompletion setups won't—so we keep it last.)
    "gpt-5",
]

# Error classes may differ between SDK versions; handle generically.
def _is_retryable_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(s in msg for s in [
        "rate limit", "timeout", "overloaded", "server error", "temporarily unavailable",
        "connection reset", "connection aborted", "read timed out", "504", "502", "503"
    ])

def _chat_completion_with_retries(messages, max_tokens, temperature, top_p,
                                  frequency_penalty, presence_penalty,
                                  max_attempts=6):
    # exponential backoff with jitter
    delay = 1.0
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        for model in MODEL_CANDIDATES:
            try:
                return openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    max_tokens=max_tokens,
                    timeout=60,  # legacy SDK supports this kwarg
                )
            except Exception as e:
                last_exc = e
                # If this is a hard "model not found/unsupported" error, try the next model immediately
                if "model" in str(e).lower() and any(k in str(e).lower() for k in ["not found", "does not exist", "unsupported", "unknown"]):
                    continue
                # If retryable (rate limit, timeout, transient), back off; otherwise raise
                if _is_retryable_error(e):
                    break  # break inner model loop to back off, keep same model order next attempt
                else:
                    # Non-retryable, try next model if it's obviously model-related; else raise
                    if "model" in str(e).lower():
                        continue
                    raise

        # Backoff before next attempt
        time.sleep(delay + random.uniform(0, 0.5))
        delay = min(delay * 2, 10.0)

    # If we’re here, all attempts/models failed
    raise RuntimeError(f"OpenAI ChatCompletion failed after retries: {last_exc}")

# -----------------------------
# Public function
# -----------------------------
def humanize_text(text: str, max_ratio: float = 1.10) -> str:
    """
    Rephrase AI-ish text into human-sounding academic prose with high burstiness/perplexity,
    slight redundancy, and minor non-critical imperfections—while staying within [original, 110%].
    Works on legacy OpenAI Python SDKs via Chat Completions.
    """
    src = (text or "").strip()
    if not src:
        return ""

    original_words = _wc(src)
    ceiling_words  = int(math.floor(original_words * max_ratio))

    # Tight output token budget (≈1.3 tokens/word + buffer) to avoid overrun on old SDKs
    estimated_output_tokens = int(ceiling_words * 1.3) + 64
    max_tokens = max(256, min(2000, estimated_output_tokens))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": STYLE_DEMO},  # style anchor
        {"role": "user", "content": _build_user_prompt(src, original_words, ceiling_words)},
    ]

    # Higher temperature and adjusted parameters for more creative, human-like output with high perplexity
    resp = _chat_completion_with_retries(
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.9,  # Increased for more creativity and varied output
        top_p=0.92,       # Slightly reduced to focus on high-quality diverse tokens
        frequency_penalty=0.4,  # Increased to encourage vocabulary diversity
        presence_penalty=0.3,   # Added to encourage topic diversity
    )

    out = resp.choices[0].message["content"].strip()
    out = _clean_paragraphs(out)

    # Final guardrails: enforce the word cap without hallucinating
    out_wc = _wc(out)
    if out_wc > ceiling_words:
        out = _trim_to_cap(out, ceiling_words)

    # If it somehow goes under original length, we accept as-is (no filler injected)
    return out
