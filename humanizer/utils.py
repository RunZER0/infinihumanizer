"""Utilities for routing humanization requests to supported LLM engines."""

from __future__ import annotations

import os
from typing import Callable, Dict

from .llm_engines import DeepSeekEngine, OpenAIEngine
from .llm_engines.claude_engine import humanize_text_claude

# Character limit for safety
MAX_TOTAL_CHARS = 10000


def humanize_with_claude(text: str) -> str:
    """Humanize text using the Claude engine."""
    try:
        # Claude engine expects a list, returns a list
        return humanize_text_claude([text])[0]
    except Exception as e:
        raise RuntimeError(f"Claude API error: {str(e)}")


def humanize_with_openai(text: str) -> str:
    """Humanize text using the OpenAI engine."""
    engine = OpenAIEngine()
    return engine.humanize(text, chunk_index=0)


def humanize_with_deepseek(text: str) -> str:
    """Humanize text using the DeepSeek engine."""
    engine = DeepSeekEngine()
    return engine.humanize(text, chunk_index=0)


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
