"""
Text humanization engine — paragraph-level processing.

The fine-tuned model was trained on individual paragraphs, so we:
1. Split input on paragraph boundaries (double-newline / blank line).
2. Classify each block: heading, list, citation-sentence, reference section,
   or regular paragraph.
3. Only regular paragraphs go to the fine-tuned model (one API call each).
4. Everything else is kept verbatim.
5. Reassemble in strict original order.
"""

import os
import re
import random
import concurrent.futures
from openai import OpenAI, APITimeoutError
from ..modes_config import (
    get_mode_config, format_prompt_for_mode, DEFAULT_MODE,
    get_model_id, get_model_system_prompt, AVAILABLE_MODELS, DEFAULT_MODEL,
)

# ── Citation detection ──────────────────────────────────────────────────

_CITE_PAREN = re.compile(
    r'\('
    r'(?:[A-Z][a-zA-Z\'\-]+(?:\s(?:and|&|et\s+al\.?)\s+[A-Z][a-zA-Z\'\-]+)?'
    r'(?:,?\s*(?:"[^"]+"|\'[^\']+\'))?'
    r'[,\s]*(?:\d[\d\-,\s]*|p+\.\s*\d[\d\-,\s]*)?'
    r'|"[^"]+"[,\s]*\d*)\)',
)
_CITE_BRACKET = re.compile(r'\[\d+(?:[,\-–]\s*\d+)*\]')

_WORKS_CITED_HEADER = re.compile(
    r'^(Works?\s+Cited|References|Bibliography|Works?\s+Consulted)\s*$',
    re.IGNORECASE | re.MULTILINE,
)

# ── Block classification helpers ────────────────────────────────────────

_LIST_BULLET = re.compile(r'^\s*(?:[-•*]|\d+[.)]\s|[a-z][.)]\s|[ivxIVX]+[.)]\s)', re.MULTILINE)


def _is_heading(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    lines = stripped.splitlines()
    if len(lines) > 2:
        return False
    words = stripped.split()
    return len(words) < 15 and not stripped.rstrip().endswith('.')


def _is_list(block: str) -> bool:
    lines = [ln for ln in block.strip().splitlines() if ln.strip()]
    if len(lines) < 2:
        return False
    bullet_count = sum(1 for ln in lines if _LIST_BULLET.match(ln))
    return bullet_count >= len(lines) * 0.5


def _is_reference_section(block: str) -> bool:
    return bool(_WORKS_CITED_HEADER.match(block.strip()))


def _sentence_has_citation(sentence: str) -> bool:
    return bool(_CITE_PAREN.search(sentence)) or bool(_CITE_BRACKET.search(sentence))


def _block_is_all_citations(block: str) -> bool:
    """True if every sentence in the block contains a citation."""
    sentences = re.split(r'(?<=[.!?])\s+', block.strip())
    if not sentences:
        return False
    return all(_sentence_has_citation(s) for s in sentences if s.strip())


def _split_citation_sentences(block: str):
    """
    Split a paragraph into runs of citation-sentences vs plain sentences.
    Returns list of (text, should_humanize) tuples.
    """
    # Split on sentence boundaries while keeping the delimiter
    parts = re.split(r'(?<=[.!?])\s+', block.strip())
    if not parts:
        return [(block, True)]

    runs = []
    current = []
    current_is_cite = _sentence_has_citation(parts[0])

    for sentence in parts:
        has_cite = _sentence_has_citation(sentence)
        if has_cite == current_is_cite:
            current.append(sentence)
        else:
            runs.append((' '.join(current), not current_is_cite))
            current = [sentence]
            current_is_cite = has_cite
    if current:
        runs.append((' '.join(current), not current_is_cite))

    return runs


# ── Paragraph splitter ──────────────────────────────────────────────────

def _split_paragraphs(text: str) -> list[str]:
    """
    Split text on paragraph boundaries (blank lines).
    Preserves the exact whitespace pattern for faithful reassembly.
    """
    blocks = re.split(r'(\n\s*\n)', text)
    # blocks is alternating [content, separator, content, separator, …]
    result = []
    for b in blocks:
        if b.strip():
            result.append(b)
    return result


def _paragraph_separators(text: str) -> list[str]:
    """Return the separators between paragraphs so we can re-stitch exactly."""
    return re.findall(r'\n\s*\n', text)


class TextEngine:
    """Text humanization engine — processes each paragraph individually."""

    def __init__(self, model: str = "premium"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("API key not configured")
        self.client = OpenAI(api_key=api_key, timeout=120.0, max_retries=2)
        self.model_key = model if model in AVAILABLE_MODELS else DEFAULT_MODEL
        self.model = get_model_id(self.model_key)

    # ── Single-paragraph API call ───────────────────────────────────────

    def _humanize_paragraph(self, paragraph: str, mode: str, temperature: float) -> str:
        mode_config = get_mode_config(mode)
        system_prompt = get_model_system_prompt(self.model_key)
        user_prompt = format_prompt_for_mode(mode, paragraph)

        base_temp = temperature if temperature is not None else mode_config["temperature"]
        jitter = random.uniform(-0.03, 0.03)
        final_temp = max(0.1, min(1.0, base_temp + jitter))

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=final_temp,
            max_tokens=4000,
            stream=True,
        )

        result = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                result += chunk.choices[0].delta.content
                # Repetition guard
                sentences = result.split('. ')
                if len(sentences) > 3:
                    r = sentences[-3:]
                    if r[0] == r[1] == r[2]:
                        break

        if not result.strip():
            return paragraph  # Fallback — return original
        return result.strip()

    # ── Main entry point ────────────────────────────────────────────────

    def humanize(self, text: str, mode: str = None, temperature: float = None) -> str:
        if not mode:
            mode = DEFAULT_MODE

        paragraphs = _split_paragraphs(text)
        separators = _paragraph_separators(text)

        if not paragraphs:
            return text

        # Classify each paragraph → (index, text, should_humanize)
        tasks: list[tuple[int, str, bool]] = []
        in_references = False

        for idx, block in enumerate(paragraphs):
            stripped = block.strip()

            # Once we hit a Works Cited header, everything after is verbatim
            if _is_reference_section(stripped):
                in_references = True

            if in_references:
                tasks.append((idx, block, False))
                continue

            if _is_heading(stripped):
                tasks.append((idx, block, False))
                continue

            if _is_list(stripped):
                tasks.append((idx, block, False))
                continue

            if _block_is_all_citations(stripped):
                tasks.append((idx, block, False))
                continue

            # For mixed paragraphs (some sentences have citations, some don't)
            # split into runs, humanize only the plain runs, then stitch back
            runs = _split_citation_sentences(stripped)
            has_mixed = any(not h for _, h in runs) and any(h for _, h in runs)

            if has_mixed:
                # Mark for special mixed handling
                tasks.append((idx, block, "mixed"))
            else:
                tasks.append((idx, block, True))

        # ── Parallel processing ─────────────────────────────────────────
        results: dict[int, str] = {}

        def _process(idx: int, block: str):
            try:
                return idx, self._humanize_paragraph(block.strip(), mode, temperature)
            except Exception as exc:
                raise RuntimeError(f"Paragraph {idx} failed: {exc}") from exc

        def _process_mixed(idx: int, block: str):
            """Humanize only the non-citation sentences within a paragraph."""
            runs = _split_citation_sentences(block.strip())
            out_parts = []
            for run_text, should_h in runs:
                if should_h and run_text.strip():
                    try:
                        out_parts.append(self._humanize_paragraph(run_text, mode, temperature))
                    except Exception:
                        out_parts.append(run_text)
                else:
                    out_parts.append(run_text)
            return idx, ' '.join(out_parts)

        to_humanize = [(idx, blk) for idx, blk, flag in tasks if flag is True]
        to_mixed    = [(idx, blk) for idx, blk, flag in tasks if flag == "mixed"]
        verbatim    = {idx: blk for idx, blk, flag in tasks if flag is False}

        results.update(verbatim)

        # Run all API calls in parallel (max 5 workers for rate limits)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = []
            for idx, blk in to_humanize:
                futures.append(pool.submit(_process, idx, blk))
            for idx, blk in to_mixed:
                futures.append(pool.submit(_process_mixed, idx, blk))

            for fut in concurrent.futures.as_completed(futures):
                idx, humanized = fut.result()
                results[idx] = humanized

        # ── Reassemble in original order ────────────────────────────────
        ordered = [results[i] for i in range(len(paragraphs))]

        # Stitch with original separators
        out = ordered[0]
        for i, para in enumerate(ordered[1:], start=1):
            sep = separators[i - 1] if i - 1 < len(separators) else "\n\n"
            out += sep + para

        return out
