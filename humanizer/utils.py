"""Utilities for routing humanization requests to supported LLM engines."""

import os
from typing import Callable, Dict

from .llm_engines import DeepSeekEngine, OpenAIEngine
from .llm_engines.claude_engine import humanize_text_claude


def humanize_with_claude(text: str, chunk_index: int = 0) -> str:
    """Humanize text using the Claude engine."""

    return humanize_text_claude([text])[0]


def humanize_with_openai(text: str, chunk_index: int = 0) -> str:
    """Humanize text using the OpenAI engine."""

    engine = OpenAIEngine()
    return engine.humanize(text, chunk_index)


def humanize_with_deepseek(text: str, chunk_index: int = 0) -> str:
    """Humanize text using the DeepSeek engine."""

    engine = DeepSeekEngine()
    return engine.humanize(text, chunk_index)


ENGINE_HANDLERS: Dict[str, Callable[[str, int], str]] = {
    "claude": humanize_with_claude,
    "openai": humanize_with_openai,
    "deepseek": humanize_with_deepseek,
}


def humanize_text(text: str, engine: str | None = None) -> str:
    """Main entry point for text humanization."""

    chosen = (engine or os.environ.get("HUMANIZER_ENGINE") or "claude").lower()
    return humanize_text_with_engine(text, chosen)


def humanize_text_with_engine(text: str, engine: str) -> str:
    """Route the request to the selected LLM engine."""

    engine = engine.lower()
    if engine not in ENGINE_HANDLERS:
        raise ValueError(f"Unknown engine: {engine}")
    return humanize_full_text(text, engine)


def humanize_full_text(text: str, engine: str) -> str:
    """Send the entire input to the specified engine without chunking."""

    handler = ENGINE_HANDLERS[engine]
    return handler(text, 0)

