"""Utilities for routing humanization requests to supported LLM engines."""

from __future__ import annotations

import os
from typing import Callable, Dict

from .chunking import TextChunker, TextRejoiner
from .llm_engines import DeepSeekEngine, OpenAIEngine
from .llm_engines.claude_engine import humanize_text_claude

# Chunking configuration (fixed 500 words per chunk, always enabled)
CHUNKING_ENABLED = True
CHUNK_MIN_SIZE = 500
CHUNK_MAX_SIZE = 500
CHUNKING_THRESHOLD = 500  # Always chunk at 500 words


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
    """Route to the appropriate LLM engine with intelligent chunking."""

    engine = engine.lower()
    if engine not in ENGINE_HANDLERS:
        raise ValueError(f"Unknown engine: {engine}")
    return humanize_with_chunking(text, engine)


def humanize_with_chunking(text: str, engine: str) -> str:
    """Humanize text by processing it in fixed-size chunks."""

    chunker = TextChunker(
        min_chunk_size=CHUNK_MIN_SIZE,
        max_chunk_size=CHUNK_MAX_SIZE,
        overlap_sentences=2,
    )
    rejoiner = TextRejoiner()
    chunks = chunker.chunk_text(text)
    processed_chunks = []

    handler = ENGINE_HANDLERS[engine]

    for chunk in chunks:
        chunk_input = (
            f"{chunk.overlap_start}\n\n{chunk.text}"
            if chunk.has_overlap_start
            else chunk.text
        )
        try:
            processed_text = handler(chunk_input, chunk.index)
            print(f"  ✅ Chunk {chunk.index + 1} processed ({len(processed_text)} chars)")
            processed_chunks.append((chunk, processed_text))
        except Exception as error:
            print(f"  ⚠️ Chunk {chunk.index + 1} failed, retrying: {error}")
            try:
                processed_text = handler(chunk_input, chunk.index)
                print(f"  ✅ Chunk {chunk.index + 1} retry successful")
                processed_chunks.append((chunk, processed_text))
            except Exception as retry_error:
                print(f"  ❌ Chunk {chunk.index + 1} failed permanently: {retry_error}")
                raise RuntimeError(
                    f"Failed to process chunk {chunk.index}: {retry_error}"
                ) from retry_error

    print(f"🔗 Rejoining {len(processed_chunks)} chunks...")
    rejoined_text = rejoiner.rejoin_chunks(processed_chunks)
    print(f"✅ Chunks rejoined - Text: {len(rejoined_text)} chars")
    print(f"✅ CHUNKING COMPLETE - Final text: {len(rejoined_text)} chars\n")
    return rejoined_text

