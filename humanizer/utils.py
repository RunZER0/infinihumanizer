import os
import re
import math
from openai import OpenAI

# Use the new OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------- utilities ----------
_WORD_RE = re.compile(r"\b\w+\b")

def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))

def trim_to_cap(text: str, cap_words: int) -> str:
    words = text.split()
    if len(words) <= cap_words:
        return text.strip()
    cut = " ".join(words[:cap_words]).strip()
    # try to end cleanly at a sentence boundary
    last_period = cut.rfind(".")
    if last_period > 0:
        return cut[:last_period + 1].strip()
    return cut

# ---------- prompts ----------
SYSTEM_PROMPT = """
You are an academic rephraser.

Non-negotiables (in order):
1) Fidelity: Preserve every claim, quote, citation, number, and technical term. Do not add sources or facts.
2) Academic tone: Formal, precise, cohesive; no slang or hype.
3) Human texture:
   • Burstiness: Mix short and long sentences (target ≥25% ≤12 words; ≥15% ≥28 words).
   • Perplexity: Prefer specific nouns and concrete verbs; avoid stock transitions.
   • Slight redundancy: 1–2 gentle reiterations per ~300 words for emphasis.
   • Minor imperfections: allow ~1 small, non-critical grammatical slip per 200–300 words (never inside quotes, numbers, titles, equations, or technical terms).
4) Organization: Reorder for clarity; do not paraphrase line-by-line; remove filler and redundancies.
5) Banned exact phrases: furthermore, moreover, in addition, it is important to note, one can see, this shows.

Respect the word cap the user provides.
Output only the rewritten text. No prefaces, no lists, no JSON.
""".strip()

# A tiny style anchor to reinforce cadence and confidence without being heavy-handed
STYLE_DEMO = """
Source (excerpt):
AI systems significantly influence writing workflows. It is important to note that authors should adapt.

Humanized academic rewrite (style to imitate):
AI now shapes how we draft, revise, and substantiate arguments. Writers do not need panic; they need methods. Learn the tools, keep your evidence straight, and deliver work that reads clean yet alive.
""".strip()

def build_user_prompt(src: str, original_words: int, ceiling_words: int) -> str:
    return (
        f"ORIGINAL_WORDS={original_words}\n"
        f"CEILING_WORDS={ceiling_words}\n\n"
        "Rephrase the text below per the constraints. Preserve meaning, quotes, numbers, and technical terms exactly. "
        "Maintain formal academic tone, high burstiness/perplexity, slight redundancy, and allow only minor, non-critical imperfections. "
        "Output only the rewritten text.\n\n"
        f"TEXT:\n{src.strip()}"
    )

# ---------- main function ----------
def humanize_text(text: str, max_ratio: float = 1.10, model: str = "gpt-5") -> str:
    """
    Rephrase AI-y text into human-sounding academic prose with high burstiness/perplexity,
    slight redundancy, and minor non-critical imperfections. Keeps length within [original, 110%].
    """
    src = text.strip()
    if not src:
        return ""

    original_words = word_count(src)
    ceiling_words = int(math.floor(original_words * max_ratio))

    # Tight max_tokens based on ceiling words (≈1.3 tokens per word + small buffer)
    estimated_output_tokens = int(ceiling_words * 1.3) + 64
    max_tokens = max(256, min(2000, estimated_output_tokens))

    def call_once(ow: int, cw: int) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": STYLE_DEMO},  # style anchor
            {"role": "user", "content": build_user_prompt(src, ow, cw)},
        ]
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,            # variety without chaos
            top_p=0.95,
            frequency_penalty=0.2,      # nudges away from repetition
            presence_penalty=0.0,
            max_tokens=max_tokens,
        )
        out = resp.choices[0].message.content.strip()
        # clean stray excessive blank lines
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out

    # First attempt
    result = call_once(original_words, ceiling_words)
    out_wc = word_count(result)

    # One retry if out of bounds (below original or above ceiling)
    if out_wc < original_words or out_wc > ceiling_words:
        # Nudge the cap if needed to coax compliance, but never above the real ceiling
        target_ceiling = ceiling_words if out_wc <= ceiling_words else max(original_words, min(ceiling_words, out_wc - 10))
        result = call_once(original_words, target_ceiling)
        out_wc = word_count(result)

    # Final hard guard: trim to cap; if still short, return as-is (do not hallucinate)
    if out_wc > ceiling_words:
        result = trim_to_cap(result, ceiling_words)

    return result
