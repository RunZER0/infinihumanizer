# humanize.py
import os
import re
import math

# Legacy SDK import (Chat Completions)
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
    return len(_WORD_RE.findall(s or ""))

def _trim_to_cap(text: str, cap_words: int) -> str:
    words = (text or "").split()
    if len(words) <= cap_words:
        return (text or "").strip()
    cut = " ".join(words[:cap_words]).strip()
    last_period = cut.rfind(".")
    if last_period > 0:
        return cut[:last_period+1].strip()
    return cut

def _clean_paragraphs(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", (text or "").strip())

def _sentences(text: str):
    # simple sentence split
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text or "") if s.strip()]

def _burstiness_counts(text: str):
    lens = [len(s.split()) for s in _sentences(text)]
    short = sum(1 for n in lens if n <= 7)
    long  = sum(1 for n in lens if n >= 28)
    return short, long

def _remove_en_em_dashes(text: str) -> str:
    # Replace en/em dashes with commas (safe default for most prose)
    text = (text or "").replace("—", ", ").replace("–", ", ")
    # Collapse accidental dup commas from replacement
    text = re.sub(r",\s*,+", ", ", text)
    # Normalize spaces around punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

# -----------------------------
# Prompts (rewritten to your spec)
# -----------------------------
SYSTEM_PROMPT = (
    "You are an editor who rewrites entire essays into clear, formal, and slightly simpler prose "
    "without drifting into basic or conversational style. Fully rephrase the original, maintain meaning, "
    "and allow some purposeful redundancy for emphasis.\n\n"
    "Hard requirements:\n"
    "- No en dashes (–) or em dashes (—). If a dash would be natural, use commas, semicolons, periods, or parentheses instead. "
    "Hyphens (-) are allowed only inside established compound words.\n"
    "- Burstiness: vary sentence length intentionally.\n"
    "- Tone: formal, precise, readable; not chatty; avoid florid phrasing and generic scaffolding transitions.\n"
    "- Preserve all facts, quotations, numbers, names, and citations exactly.\n"
    "- You may reorganize paragraphs to improve logic and flow.\n"
    "- Length: keep within the provided limit.\n\n"
    "Before returning, silently self-check that there are zero en/em dashes and that sentences show clear burstiness."
)

BANNED_TRANSITIONS = [
    "furthermore", "moreover", "in addition", "additionally",
    "it is important to note", "consequently", "in conclusion"
]

def _build_user_prompt(src: str, original_words: int, ceiling_words: int) -> str:
    return (
        f"ORIGINAL_WORDS={original_words}\n"
        f"CEILING_WORDS={ceiling_words}\n\n"
        "GOALS\n"
        "- Rephrase the entire essay into simpler yet formal language (not basic).\n"
        "- Allow some purposeful redundancy to reinforce key ideas.\n"
        "- Main priority: strong burstiness and zero en/em dashes.\n\n"
        "CONSTRAINTS\n"
        f"- Avoid these transitions entirely: {', '.join(BANNED_TRANSITIONS)}.\n"
        "- Sentence-length mix target (per ~400 words): at least three sentences of 7 words or fewer, "
        "and at least two sentences of 28 words or more.\n"
        "- Keep a formal tone; preserve facts, quotations, numbers, names, and citations.\n"
        f"- Stay ≤ {ceiling_words} words.\n\n"
        "DELIVERABLE\n"
        "- Output only the rewritten essay. No preface or meta-notes.\n\n"
        "ESSAY TO REWRITE\n"
        f"{src.strip()}"
    )

# -----------------------------
# Core call (GPT-4o only)
# -----------------------------
def _chat_once(messages, max_tokens: int):
    return openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.85,
        top_p=0.92,
        frequency_penalty=0.3,
        presence_penalty=0.25,
        max_tokens=max_tokens,
        request_timeout=60,  # works on legacy SDKs
    )

# -----------------------------
# Public function
# -----------------------------
def humanize_text(text: str, max_ratio: float = 1.10) -> str:
    """
    Rewrite an essay into slightly simpler yet formal prose with some redundancy,
    strong burstiness, and zero en/em dashes. Uses GPT-4o via Chat Completions.
    Output length limited to at most `max_ratio` * original words.
    """
    src = (text or "").strip()
    if not src:
        return ""

    original_words = _wc(src)
    ceiling_words  = int(math.floor(original_words * max_ratio))

    # ≈1.3 tokens/word + small buffer
    estimated_output_tokens = int(ceiling_words * 1.3) + 64
    max_tokens = max(256, min(4000, estimated_output_tokens))

    # First pass
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(src, original_words, ceiling_words)},
    ]
    resp = _chat_once(messages, max_tokens=max_tokens)
    out = resp.choices[0].message["content"].strip()

    # Post-process: clean paragraphs, enforce no en/em dashes, trim to cap
    out = _clean_paragraphs(out)
    out = _remove_en_em_dashes(out)
    out = _trim_to_cap(out, ceiling_words)

    # Burstiness safeguard: if not enough short/long sentences, request a quick revision
    short, long = _burstiness_counts(out)
    need_short = 3
    need_long  = 2
    if short < need_short or long < need_long:
        # Ask for a targeted revision to fix rhythm only; keep everything else intact
        fix_prompt = (
            "Revise the essay below to improve burstiness while preserving all content. "
            f"Ensure at least {need_short} sentences have 7 words or fewer and at least {need_long} sentences have 28 words or more. "
            "Do not introduce en dashes (–) or em dashes (—); use commas, semicolons, periods, or parentheses instead. "
            f"Stay ≤ {ceiling_words} words. Output only the revised essay.\n\n"
            "ESSAY:\n" + out
        )
        fix_resp = _chat_once(
            [
                {"role": "system", "content": "You revise text for sentence-length variation and punctuation compliance."},
                {"role": "user", "content": fix_prompt},
            ],
            max_tokens=max_tokens
        )
        out = fix_resp.choices[0].message["content"].strip()
        out = _clean_paragraphs(out)
        out = _remove_en_em_dashes(out)
        out = _trim_to_cap(out, ceiling_words)

    return out

# -----------------------------
# Simple CLI usage (optional)
# -----------------------------
if __name__ == "__main__":
    import sys, textwrap
    if sys.stdin.isatty():
        print("Paste text, then Ctrl-D (Unix) / Ctrl-Z Enter (Windows):")
    src_text = sys.stdin.read()
    result = humanize_text(src_text)
    print("\n" + result + "\n")
