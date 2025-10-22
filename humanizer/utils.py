"""Utilities for routing humanization requests to supported LLM engines."""

from __future__ import annotations

import os
import time
import gc
from typing import Callable, Dict

from .chunking import TextChunker, TextRejoiner
from .llm_engines import DeepSeekEngine, OpenAIEngine
from .llm_engines.claude_engine import humanize_text_claude

# CHUNKING CONFIGURATION - REDUCED FOR RENDER LIMITS
CHUNKING_ENABLED = True
CHUNK_MIN_SIZE = 250  # Reduced from 500
CHUNK_MAX_SIZE = 300  # Reduced from 500  
CHUNKING_THRESHOLD = 300  # Reduced from 500
MAX_TOTAL_CHARS = 8000  # Added safety limit


def humanize_with_claude(text: str, chunk_index: int = 0) -> str:
    """Humanize text using the Claude engine."""
    try:
        return humanize_text_claude([text])[0]
    except Exception as e:
        raise RuntimeError(f"Claude API error: {str(e)}")


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
    
    # SAFETY CHECK: Limit total input size
    if len(text) > MAX_TOTAL_CHARS:
        raise ValueError(f"Text too long ({len(text)} chars). Maximum allowed: {MAX_TOTAL_CHARS}")
    
    engine = engine.lower()
    if engine not in ENGINE_HANDLERS:
        raise ValueError(f"Unknown engine: {engine}")
    
    return humanize_with_chunking(text, engine)


def humanize_with_chunking(text: str, engine: str) -> str:
    """Humanize text by processing it in fixed-size chunks with memory management."""
    
    # Initialize chunker with smaller chunks
    chunker = TextChunker(
        min_chunk_size=CHUNK_MIN_SIZE,
        max_chunk_size=CHUNK_MAX_SIZE,
        overlap_sentences=1,  # Reduced overlap to save processing time
    )
    rejoiner = TextRejoiner()
    chunks = chunker.chunk_text(text)
    processed_chunks = []

    handler = ENGINE_HANDLERS[engine]
    
    print(f"📊 Processing {len(chunks)} chunks with {engine} engine...")
    
    # Process chunks with memory management
    for i, chunk in enumerate(chunks):
        chunk_input = (
            f"{chunk.overlap_start}\n\n{chunk.text}"
            if chunk.has_overlap_start
            else chunk.text
        )
        
        # Force garbage collection between chunks
        if i > 0:
            gc.collect()
        
        try:
            start_time = time.time()
            processed_text = handler(chunk_input, i)
            processing_time = time.time() - start_time
            
            print(f"  ✅ Chunk {i+1}/{len(chunks)} processed in {processing_time:.1f}s ({len(processed_text)} chars)")
            
            # Safety check: if processing takes too long, reduce future chunks
            if processing_time > 20:  # 20 seconds is getting close to timeout
                print(f"  ⚠️ Chunk {i+1} took {processing_time:.1f}s - consider reducing chunk size")
            
            processed_chunks.append((chunk, processed_text))
            
        except Exception as error:
            print(f"  ❌ Chunk {i+1} failed: {error}")
            
            # For timeout errors, provide helpful message
            if "timeout" in str(error).lower() or "timed out" in str(error).lower():
                raise RuntimeError(
                    f"Chunk {i+1} timed out. The text may be too long for Render's free tier. "
                    f"Try splitting your text into smaller sections (under {CHUNK_MAX_SIZE} words each)."
                ) from error
            else:
                raise RuntimeError(f"Failed to process chunk {i+1}: {error}") from error

    print(f"🔗 Rejoining {len(processed_chunks)} chunks...")
    rejoined_text = rejoiner.rejoin_chunks(processed_chunks)
    print(f"✅ Successfully processed {len(text)} chars → {len(rejoined_text)} chars")
    return rejoined_text
