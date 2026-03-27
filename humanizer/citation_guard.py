"""
Citation Guard — preserves MLA (and other) citations through humanization.

Strategy:
1. Extract all in-text citations and the Works Cited / References block BEFORE humanization.
2. After humanization, detect which citations were lost or mangled.
3. Re-inject missing in-text citations by matching surrounding sentence context.
4. Restore the Works Cited block verbatim (it should never be rewritten).
"""

import re
from difflib import SequenceMatcher


# ── Regex patterns for in-text citations ────────────────────────────────

# MLA parenthetical: (Smith 42), (Smith and Jones 42), (Smith et al. 42),
#   (Smith, "Title" 42), ("Title" 42), (Smith 42-45), (Smith 42, 78)
# Also APA-style: (Smith, 2020), (Smith & Jones, 2020, p. 42)
# General parenthetical with author + page/year
_CITATION_PAREN = re.compile(
    r'\('
    r'(?:'
    r'[A-Z][a-zA-Z\'\-]+'                 # Author surname
    r'(?:\s(?:and|&|et\s+al\.?)\s+'       # optional "and/& Author" or "et al."
    r'[A-Z][a-zA-Z\'\-]+)?'
    r'(?:,?\s*(?:"[^"]+"|\'[^\']+\'))?' # optional quoted title
    r'[,\s]*'
    r'(?:\d[\d\-,\s]*|(?:p+\.\s*\d[\d\-,\s]*))?'  # page numbers
    r'|'
    r'"[^"]+"'                             # Or just a quoted title
    r'[,\s]*\d*'
    r')'
    r'\)',
    re.UNICODE
)

# Footnote / endnote markers: superscript digits, or [1], [2-3], etc.
_CITATION_BRACKET = re.compile(r'\[(\d+(?:[,\-–]\s*\d+)*)\]')

# Works Cited / References / Bibliography block — everything from the header to EOF
_WORKS_CITED_HEADER = re.compile(
    r'^(Works?\s+Cited|References|Bibliography|Works?\s+Consulted)\s*$',
    re.IGNORECASE | re.MULTILINE
)


def extract_citations(text: str):
    """
    Extract in-text citations and the Works Cited block.

    Returns:
        dict with:
            "inline": list of (match_text, start_pos, end_pos) tuples
            "works_cited": the full Works Cited block as a string (or None)
            "works_cited_start": char offset where it begins (or None)
    """
    inline = []

    for m in _CITATION_PAREN.finditer(text):
        inline.append((m.group(), m.start(), m.end()))

    for m in _CITATION_BRACKET.finditer(text):
        inline.append((m.group(), m.start(), m.end()))

    # Works Cited block
    works_cited = None
    wc_start = None
    wc_match = _WORKS_CITED_HEADER.search(text)
    if wc_match:
        wc_start = wc_match.start()
        works_cited = text[wc_start:]

    return {
        "inline": inline,
        "works_cited": works_cited,
        "works_cited_start": wc_start,
    }


def _sentence_around(text: str, pos: int, radius: int = 120) -> str:
    """Return a window of text around a position for fuzzy matching."""
    start = max(0, pos - radius)
    end = min(len(text), pos + radius)
    return text[start:end]


def _find_best_insert(original: str, humanized: str, cite_text: str, orig_pos: int) -> int | None:
    """
    Find the best position in humanized text to re-insert a missing citation.
    Uses the sentence context around the original position to locate the
    corresponding spot in the humanized output.
    """
    # Get surrounding context from original
    context = _sentence_around(original, orig_pos, radius=100)

    # Try to find the sentence boundary just before the citation in the original
    before_cite = original[max(0, orig_pos - 200):orig_pos].rstrip()

    # Get the last 4-8 words before the citation — these are our anchor
    words_before = before_cite.split()[-8:]
    anchor = ' '.join(words_before)

    if not anchor:
        return None

    # Fuzzy-search for the anchor in humanized text
    best_ratio = 0.0
    best_pos = None

    # Slide a window across the humanized text
    h_words = humanized.split()
    anchor_wc = len(anchor.split())

    for i in range(len(h_words)):
        window = ' '.join(h_words[i:i + anchor_wc + 2])
        ratio = SequenceMatcher(None, anchor.lower(), window.lower()).ratio()
        if ratio > best_ratio and ratio > 0.45:
            best_ratio = ratio
            # Calculate char position after this window
            char_pos = humanized.find(window)
            if char_pos >= 0:
                best_pos = char_pos + len(window)

    return best_pos


def restore_citations(original: str, humanized: str) -> str:
    """
    Compare original and humanized text; re-inject any citations that were
    dropped during humanization.

    1. Re-attach the Works Cited block verbatim if it was lost.
    2. Re-insert any parenthetical/bracket citations that are missing.
    """
    orig_data = extract_citations(original)
    hum_data = extract_citations(humanized)

    result = humanized

    # ── Works Cited block ───────────────────────────────────────
    if orig_data["works_cited"]:
        if not hum_data["works_cited"]:
            # Entire block was dropped — append it verbatim
            result = result.rstrip() + "\n\n" + orig_data["works_cited"]
        else:
            # Block exists but may have been mangled — replace with original
            hum_wc_start = hum_data["works_cited_start"]
            result = result[:hum_wc_start].rstrip() + "\n\n" + orig_data["works_cited"]

    # ── In-text citations ───────────────────────────────────────
    existing_cites = {c[0] for c in extract_citations(result)["inline"]}

    for cite_text, orig_start, orig_end in orig_data["inline"]:
        if cite_text in existing_cites:
            # Citation survived — skip
            continue

        # Citation was dropped — try to re-insert at the right spot
        insert_pos = _find_best_insert(original, result, cite_text, orig_start)

        if insert_pos is not None:
            # Insert the citation with a space before it
            before = result[:insert_pos].rstrip()
            after = result[insert_pos:]
            # If the position lands right before a period, put citation before the period
            if after.lstrip().startswith('.'):
                after_stripped = after.lstrip()
                result = before + ' ' + cite_text + after_stripped
            else:
                result = before + ' ' + cite_text + ' ' + after.lstrip()
        else:
            # Could not find a match — append citation at end of corresponding paragraph
            # as a fallback, just note that it was preserved
            pass

        # Update existing set so we don't double-insert
        existing_cites.add(cite_text)

    return result
