"""Direct API-backed text rewriting for InfiniAI."""

from __future__ import annotations

import os
import re

from openai import OpenAI

MAX_INPUT_WORDS = 3000
MAX_INPUT_CHARS = 18000

DEFAULT_MODEL = "ft:gpt-4.1-mini-2025-04-14:ynai:hopetoo:DNkpWxS4:ckpt-step-323"

SYSTEM_PROMPT = """Rewrite the user's text in natural, economical prose.

Preserve the original meaning, facts, argument, quotations, citations, names and technical details. Keep the existing structure when it carries meaning.

Remove redundant punchline fragments, sloganized antithesis, manufactured punchiness, unnecessary negation, clipped taglines, rule-of-three phrasing, 'not X but Y' constructions, generic transitions, inflated wording, repetitive conclusions and sentences that merely restate the previous sentence with attitude.

Once a sentence has delivered the meaning, stop. Every sentence must add information or necessary nuance. Do not invent claims, examples or sources. Return only the rewritten text."""


def _clean_output(text: str) -> str:
    cleaned = (text or "").strip()
    prefixes = (
        "Here is the rewritten text:",
        "Here's the rewritten text:",
        "Rewritten text:",
        "Here is the humanized text:",
        "Humanized text:",
    )
    for prefix in prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].lstrip()
            break
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def rewrite_text(text: str, temperature: float = 0.65) -> str:
    text = (text or "").strip()
    if not text:
        raise ValueError("Add text to rewrite.")
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(f"Text exceeds the {MAX_INPUT_CHARS:,}-character limit.")
    word_count = len(text.split())
    if word_count > MAX_INPUT_WORDS:
        raise ValueError(f"Text exceeds the {MAX_INPUT_WORDS:,}-word limit.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Humanizer API is not configured.")

    model = os.environ.get("HUMANIZER_MODEL_ID", DEFAULT_MODEL)
    temperature = max(0.1, min(1.0, float(temperature)))

    client = OpenAI(api_key=api_key, timeout=180.0, max_retries=2)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=temperature,
        max_tokens=5000,
    )
    content = response.choices[0].message.content if response.choices else ""
    result = _clean_output(content)
    if not result:
        raise RuntimeError("The humanizer returned an empty response.")
    return result
