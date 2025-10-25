"""Utilities for routing humanization requests to supported LLM engines."""

from __future__ import annotations

import os
import re
from typing import Callable, Dict

from .llm_engines import DeepSeekEngine, OpenAIEngine
from .llm_engines.claude_engine import humanize_text_claude

# Character limit for safety
MAX_TOTAL_CHARS = 10000


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
    ]
    
    for pattern in prefix_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove trailing metadata sections that appear after double newline
    # Only remove if followed by these specific keywords at the start of a new paragraph
    metadata_keywords = ['Note:', 'Please note:', 'I hope this helps', 'Let me know', 
                        'Feel free', 'If you need', 'Important:']
    
    for keyword in metadata_keywords:
        # Remove from double newline + keyword to end of text
        pattern = r'\n\n' + re.escape(keyword) + r'.*$'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    return cleaned.strip()


def humanize_with_claude(text: str) -> str:
    """Humanize text using the Claude engine."""
    try:
        # Claude engine expects a list, returns a list
        result = humanize_text_claude([text])[0]
        return clean_llm_output(result)
    except Exception as e:
        raise RuntimeError(f"Claude API error: {str(e)}")


def humanize_with_openai(text: str) -> str:
    """Humanize text using the OpenAI engine."""
    engine = OpenAIEngine()
    result = engine.humanize(text, chunk_index=0)
    return clean_llm_output(result)


def humanize_with_deepseek(text: str) -> str:
    """Humanize text using the DeepSeek engine."""
    engine = DeepSeekEngine()
    result = engine.humanize(text, chunk_index=0)
    return clean_llm_output(result)


ENGINE_HANDLERS: Dict[str, Callable[[str], str]] = {
    "claude": humanize_with_claude,
    "openai": humanize_with_openai,
    "deepseek": humanize_with_deepseek,
}


def humanize_text(text: str, engine: str | None = None) -> str:
    """Main entry point for text humanization."""
    chosen = (engine or os.environ.get("HUMANIZER_ENGINE") or "claude").lower()
    return humanize_text_with_engine(text, chosen)


def humanize_text_with_engine(text: str, engine: str) -> str:
    """Route to the appropriate LLM engine - NO CHUNKING."""
    
    # SAFETY CHECK: Limit total input size
    if len(text) > MAX_TOTAL_CHARS:
        raise ValueError(f"Text too long ({len(text)} chars). Maximum allowed: {MAX_TOTAL_CHARS}")
    
    engine = engine.lower()
    if engine not in ENGINE_HANDLERS:
        raise ValueError(f"Unknown engine: {engine}")
    
    # Direct call to engine - no chunking
    handler = ENGINE_HANDLERS[engine]
    print(f"🚀 Processing with {engine} engine (no chunking)...")
    
    try:
        humanized_text = handler(text)
        print(f"✅ Successfully processed {len(text)} → {len(humanized_text)} chars")
        return humanized_text
    except Exception as error:
        print(f"❌ Engine failed: {error}")
        raise
