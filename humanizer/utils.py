"""Utilities for routing humanization requests."""

from __future__ import annotations

import os
import re
from typing import Callable, Dict

from .llm_engines.openai_engine import TextEngine

# Character limit for safety (increased for 2500 word support)
MAX_TOTAL_CHARS = 30000



def clean_llm_output(text: str) -> str:
    """
    Clean LLM output by removing common metadata patterns.
    Ensures only the humanized text is returned.
    """
    cleaned = text.strip()
    
    # Remove common prefixes that LLMs might add
    prefix_patterns = [
        r'^(Here is the transformed text:|Here\'s the transformed output:|Transformed text:|Output:)\s*',
        r'^(The transformed version is:|Here is the humanized text:|Humanized output:)\s*',
        r'^(Here\'s the rewritten text:|I\'ve rewritten this as:|Rewritten version:)\s*',
        r'^(This can be rewritten as:|Here\'s a rewrite:|The rewrite:)\s*',
    ]
    
    for pattern in prefix_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove trailing metadata sections that appear after double newline
    # Construct single alternation pattern for efficiency
    metadata_keywords = [
        'Note:', 'Please note:', 'I hope this helps', 'Let me know',
        'Feel free', 'If you need', 'Important:'
    ]
    
    # Build alternation pattern: (keyword1|keyword2|...)
    escaped_keywords = [re.escape(kw) for kw in metadata_keywords]
    metadata_pattern = r'\n\n(' + '|'.join(escaped_keywords) + r').*$'
    cleaned = re.sub(metadata_pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove meta-commentary patterns that indicate incomplete transformation
    # These are patterns where the LLM stops early and adds commentary
    meta_commentary_patterns = [
        r'\[Continued transformation would follow.*?\]',
        r'\[The remaining text would be transformed.*?\]',
        r'\[Rest of the text would be transformed.*?\]',
        r'\[The transformation would continue.*?\]',
        r'\[Following the same pattern.*?\]',
        r'\[And so on.*?\]',
        r'\[etc\.\]',
        r'\.\.\.[^.]*?would follow.*?$',
        r'\.\.\.[^.]*?same.*?rules.*?$',
        r'\.\.\.[^.]*?pattern.*?continues.*?$',
    ]
    
    for pattern in meta_commentary_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove trailing ellipsis followed by explanatory text
    cleaned = re.sub(r'\.\.\.\s*\(.*?\)$', '', cleaned, flags=re.DOTALL)
    
    return cleaned.strip()


def humanize_with_text_engine(text: str, mode: str = "recommended") -> str:
    """
    Humanize text using the custom model with specified mode.
    
    Args:
        text: Text to humanize
        mode: Humanization mode (recommended, readability, formal, conversational, informal, academic)
    """
    engine = TextEngine()
    result = engine.humanize(text, mode=mode)
    return clean_llm_output(result)


ENGINE_HANDLERS: Dict[str, Callable] = {
    "openai": humanize_with_text_engine,
}


def humanize_text(text: str, engine: str | None = None, mode: str = "recommended") -> str:
    """Main entry point for text humanization."""
    chosen = (engine or os.environ.get("HUMANIZER_ENGINE") or "openai").lower()
    return humanize_text_with_engine(text, chosen, mode=mode)


def humanize_text_with_engine(text: str, engine: str, mode: str = "recommended") -> str:
    """Route to the appropriate processing handler - NO CHUNKING."""
    
    # SAFETY CHECK: Limit total input size
    if len(text) > MAX_TOTAL_CHARS:
        raise ValueError(f"Text too long ({len(text)} chars). Maximum allowed: {MAX_TOTAL_CHARS}")
    
    engine = engine.lower()
    if engine not in ENGINE_HANDLERS:
        raise ValueError(f"Invalid request")
    
    # Direct call to handler - no chunking
    handler = ENGINE_HANDLERS[engine]
    print(f"🚀 Processing text (mode: {mode})...")
    
    try:
        humanized_text = handler(text, mode=mode)
        print(f"✅ Successfully processed {len(text)} → {len(humanized_text)} chars")
        return humanized_text
    except Exception as error:
        print(f"❌ Processing failed: {error}")
        raise
