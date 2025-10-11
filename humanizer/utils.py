# humanize_ua_style.py
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
    # collapse 3+ newlines to exactly two
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

def _strip_banned_transitions(text: str, banned) -> str:
    out = text or ""
    for phrase in banned:
        out = re.sub(rf"(^|\.\s+){re.escape(phrase)}[, ]", r"\1", out, flags=re.IGNORECASE)
    return out

# -----------------------------
# Style fixtures (rich context)
# -----------------------------
STYLE_NOTES = """
STYLE NOTES (for the entire rewrite)
- Voice: formal, clear, readable; not flowery; not chatty. Allow purposeful redundancy for emphasis.
- Rhythm: mix compact sentences with a few long, layered sentences. Include occasional short emphatic lines (e.g., “This is important.”).
- Diction: straightforward academic vocabulary; avoid jargon and ornate transitions. Prefer “However,” “Yet,” “Still,” when needed.
- Cohesion: begin paragraphs with strong topic sentences; follow with support and brief synthesis.
- Ethics: preserve all facts, quotations, numbers, names, and citations exactly as given in the source text.
- Punctuation: do not use en dashes (–) or em dashes (—). If a dash would be natural, prefer commas, semicolons, periods, or parentheses.
- Works Cited/References: if present in the source, keep them intact and at the end.
"""

# Expanded, short excerpts that demonstrate cadence, paragraph shape, and restraint.
STYLE_EXEMPLARS = [
    # A — President’s Mansion: thesis + solemn cadence
    """STYLE EXAMPLE A
The University of Alabama’s President’s Mansion stands as a symbol of prestige and a complicated history. Built in 1841, it has seen triumph and struggle. The building is not only a residence for leaders but also a reminder of slavery and segregation. It reflects the broader fight for racial justice. This matters.
""",
    # B — Echoes of Connection: genre rationale, audience focus
    """STYLE EXAMPLE B
It had to be a short story to give a human shape to the history of communication. Fiction invites readers into theme through character and event rather than facts. The lens connects past innovations to the present. The goal is clarity and impact.
""",
    # C — Van Gogh vs. Lange: clean compare/contrast and medium-aware claims
    """STYLE EXAMPLE C
Van Gogh’s self-portrait builds emotion through color and texture. Lange’s photograph offers a direct, factual view of hardship. One is private feeling. The other is public record. Composition guides attention in both.
""",
    # D — Structural argument (Nobody): systems-first framing
    """STYLE EXAMPLE D
Economic inequality breaks the promises of citizenship. Housing, education, and law work together to exclude the poor and the marginalized. These are structural barriers, not isolated errors. The pattern is historical and ongoing.
""",
    # E — American myth-making: thesis → consequence
    """STYLE EXAMPLE E
Myths shape national consciousness. Legendary stories about founders build identity while hiding uncomfortable truths. They justify expansion and erase violence. Seeing this clearly lets us read literature and history for what they do, not only what they say.
""",
    # F — Film analysis (The Pursuit of Happyness): shot detail + synthesis
    """STYLE EXAMPLE F
Tight close-ups reveal doubt and brief joy. Wide shots place the protagonist as a small figure in crowded space, stressing isolation and scale. Music turns brighter as prospects improve. Technique supports theme: resilience within structural limits.
""",
    # G — President’s Mansion: praxis suggestions in concrete, calm prose
    """STYLE EXAMPLE G
Clear interpretation helps visitors think deeply. Plaques, guided tours, and digital archives could name enslaved builders and workers. Doing so would expand the story, not erase it. Memory requires context.
""",
    # H — Myth/race unit: quote-handling inside analysis
    """STYLE EXAMPLE H
Wheatley writes of redemption to claim equal intellect and morality. Douglass insists, “Once you learn to read, you will be forever free.” Quotations anchor claims. Analysis does the rest.
""",
    # I — Echoes of Connection: affordances and distribution
    """STYLE EXAMPLE I
The short story is accessible and distributable. It turns abstract ideas into concrete scenes. A simple voice broadens the audience. Narrative pacing keeps attention while preserving key moments.
""",
    # J — Campus resources: pragmatic academic tone
    """STYLE EXAMPLE J
The Capstone Center offers advising, tutoring, and workshops. Crimson Closet provides professional attire for interviews. The Writing Center supports drafts and revision. Use these often. It helps.
""",
    # K — Compare/contrast wrap: tidy synthesis
    """STYLE EXAMPLE K
Both works treat the human condition. One dives inward with expressive color. The other documents outward struggle with stark realism. Different routes, similar power.
""",
    # L — Systems claim → call to action
    """STYLE EXAMPLE L
Personal effort matters. Systems still set the terms. If we want equal protection to mean something, change must be structural. Say it plainly.
""",
]

BANNED_TRANSITIONS = [
    "furthermore", "moreover", "in addition", "additionally",
    "it is important to note", "consequently", "in conclusion"
]

# -----------------------------
# Prompts
# -----------------------------
SYSTEM_PROMPT = (
    "You are an editor who rewrites entire essays into clear, formal, slightly simpler prose "
    "without drifting into basic or conversational style. Fully rephrase the original while preserving meaning, "
    "facts, quotations, numbers, names, and citations exactly. You may reorganize paragraphs for logic and flow.\n\n"
    "Hard requirements:\n"
    "- No en dashes (–) or em dashes (—). If a dash would be natural, use commas, semicolons, periods, or parentheses instead. "
    "Hyphens are allowed inside established compounds.\n"
    "- Show sentence-length variation (burstiness). Include a few short, emphatic sentences across the piece.\n"
    "- Keep a formal, precise tone. Avoid florid phrasing, clichés, and generic scaffolding transitions.\n"
    "- Maintain or slightly compress length within the given limit.\n\n"
    "Before returning, silently self-check that there are zero en/em dashes, banned transitions are not used, "
    "and that the rhythm mixes short and long sentences clearly."
)

def _build_user_prompt(src: str, original_words: int, ceiling_words: int, extra_samples=None) -> str:
    samples = STYLE_EXEMPLARS + (extra_samples or [])
    samples_block = "\n".join(samples)
    banned = ", ".join(BANNED_TRANSITIONS)
    return (
        f"ORIGINAL_WORDS={original_words}\n"
        f"CEILING_WORDS={ceiling_words}\n\n"
        "GOAL\n"
        "- Rephrase the entire essay into simpler yet formal prose (not basic), mirroring the cadence, paragraph shape, and restraint seen in the STYLE EXAMPLES.\n\n"
        "STYLE CONTEXT\n"
        f"{STYLE_NOTES.strip()}\n\n"
        "STYLE EXEMPLARS\n"
        f"{samples_block.strip()}\n\n"
        "CONSTRAINTS\n"
        f"- Avoid these transitions entirely: {banned}.\n"
        "- Sentence-length mix target (per ~400 words): at least three sentences of 7 words or fewer, and at least two sentences of 28+ words.\n"
        "- Preserve all facts, quotations, numbers, names, and citations as-is.\n"
        f"- Stay ≤ {ceiling_words} words.\n\n"
        "DELIVERABLE\n"
        "- Output only the rewritten essay. No prefaces, headings, or meta-notes.\n\n"
        "ESSAY TO REWRITE\n"
        f"{src.strip()}"
    )

# -----------------------------
# Core call (GPT-4o only)
# -----------------------------
def _chat_once(messages, max_tokens: int):
    return openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.6,
        top_p=0.92,
        frequency_penalty=0.3,
        presence_penalty=0.25,
        max_tokens=max_tokens,
        request_timeout=60,  # works on legacy SDKs
    )

# -----------------------------
# Public function
# -----------------------------
def humanize_text(text: str, max_ratio: float = 1.10, extra_style_samples=None) -> str:
    """
    Rewrite an essay into slightly simpler yet formal prose with purposeful redundancy,
    strong burstiness, and zero en/em dashes. Uses GPT-4o via Chat Completions.
    Output length limited to at most `max_ratio` * original words.

    Optionally pass `extra_style_samples` as a list of short strings to augment the STYLE EXEMPLARS.
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
        {"role": "user", "content": _build_user_prompt(src, original_words, ceiling_words, extra_style_samples)},
    ]
    resp = _chat_once(messages, max_tokens=max_tokens)
    out = resp.choices[0].message["content"].strip()

    # Post-process: clean paragraphs, enforce no en/em dashes, trim to cap, strip banned transitions
    out = _clean_paragraphs(out)
    out = _remove_en_em_dashes(out)
    out = _strip_banned_transitions(out, BANNED_TRANSITIONS)
    out = _trim_to_cap(out, ceiling_words)

    # Burstiness safeguard: if not enough short/long sentences, request a micro revision
    short, long = _burstiness_counts(out)
    need_short = 3
    need_long  = 2
    if short < need_short or long < need_long:
        fix_prompt = (
            "Revise the essay below to improve sentence-length variation while preserving all content exactly. "
            f"Ensure at least {need_short} sentences have 7 words or fewer and at least {need_long} sentences have 28 words or more. "
            "Do not introduce en dashes (–) or em dashes (—); use commas, semicolons, periods, or parentheses instead. "
            "Remove any banned transitions (furthermore, moreover, in addition, additionally, it is important to note, consequently, in conclusion). "
            f"Stay ≤ {ceiling_words} words. Output only the revised essay.\n\n"
            "ESSAY:\n" + out
        )
        fix_resp = _chat_once(
            [
                {"role": "system", "content": "You revise text for rhythm (burstiness) and punctuation compliance without changing facts or citations."},
                {"role": "user", "content": fix_prompt},
            ],
            max_tokens=max_tokens
        )
        out = fix_resp.choices[0].message["content"].strip()
        out = _clean_paragraphs(out)
        out = _remove_en_em_dashes(out)
        out = _strip_banned_transitions(out, BANNED_TRANSITIONS)
        out = _trim_to_cap(out, ceiling_words)

    return out

# -----------------------------
# Simple CLI usage (optional)
# -----------------------------
if __name__ == "__main__":
    import sys
    if sys.stdin.isatty():
        print("Paste text, then Ctrl-D (Unix) / Ctrl-Z Enter (Windows):")
    src_text = sys.stdin.read()
    result = humanize_text(src_text)
    print("\n" + result + "\n")
