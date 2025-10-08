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
    "You are an academic rephraser.\n\n"
    "Constraints:\n"
    "- Preserve all facts, quotes, citations, numbers, and technical terms exactly.\n"
    "- Maintain a formal academic tone (no slang or hype).\n"
    "- Aim for a human feel: varied sentence lengths (mix short and long), precise nouns/verbs,\n"
    "  light natural redundancy for emphasis, and allow a very small non-critical grammatical slip\n"
    "  if it sounds natural (never inside quotations, numbers, titles, equations, or technical terms).\n"
    "- Avoid these exact phrases: furthermore, moreover, in addition, it is important to note, one can see, this shows.\n"
    "- Reorganize for clarity; do not paraphrase sentence-by-sentence.\n"
    "- Respect the word cap provided by the user.\n\n"
    "Output only the rewritten text. No prefaces, no lists, no JSON."
)

STYLE_DEMO = (
    "Source (excerpt):\n"
    "AI systems significantly influence writing workflows. It is important to note that authors should adapt.\n\n"
    "Humanized academic rewrite (style to imitate):\n"
    "AI now shapes how we draft, revise, and substantiate arguments. Writers do not need panic; they need methods. "
    "Learn the tools, keep your evidence straight, and deliver work that reads clean yet alive."
)

def _build_user_prompt(src: str, original_words: int, ceiling_words: int) -> str:
    return (
        f"ORIGINAL_WORDS={original_words}\n"
        f"CEILING_WORDS={ceiling_words}\n\n"
        "Rephrase the text below per the constraints, keeping a formal academic tone, high burstiness/perplexity, "
        "slight natural redundancy, and only minor non-critical imperfections. Output only the rewritten text.\n\n"
        f"TEXT:\n{src.strip()}"
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

    # Lower randomness to prioritize instruction-following on legacy endpoints
    resp = _chat_completion_with_retries(
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.6,
        top_p=0.95,
        frequency_penalty=0.2,
        presence_penalty=0.0,
    )

    out = resp.choices[0].message["content"].strip()
    out = _clean_paragraphs(out)

    # Final guardrails: enforce the word cap without hallucinating
    out_wc = _wc(out)
    if out_wc > ceiling_words:
        out = _trim_to_cap(out, ceiling_words)

    # If it somehow goes under original length, we accept as-is (no filler injected)
    return out
