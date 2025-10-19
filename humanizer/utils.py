"""
Text Humanization Utilities
Main interface for humanizing text using LLM engines.
Supports intelligent chunking for large texts.
"""

import os
from .llm_engines import GeminiEngine, OpenAIEngine, DeepSeekEngine
from .llm_engines.claude_engine import humanize_text_claude
from .chunking import TextChunker, TextRejoiner


# Chunking configuration
CHUNKING_ENABLED = os.environ.get("ENABLE_CHUNKING", "True").lower() == "true"
CHUNK_MIN_SIZE = int(os.environ.get("CHUNK_MIN_SIZE", "200"))
CHUNK_MAX_SIZE = int(os.environ.get("CHUNK_MAX_SIZE", "400"))
CHUNKING_THRESHOLD = int(os.environ.get("CHUNKING_THRESHOLD", "500"))  # Words before chunking kicks in


def humanize_text(text: str, engine: str | None = None) -> str:
    """
    Main entry point for text humanization.
    All humanization happens via LLM APIs - no local processing.
    Automatically chunks large texts for better processing.
    
    Args:
        text: The text to humanize
        engine: Engine to use ('gemini' or 'openai'). 
                Defaults to HUMANIZER_ENGINE env var or 'gemini'
    
    Returns:
        Humanized text from the selected LLM engine
        
    Raises:
        ValueError: If engine is not recognized
        RuntimeError: If API keys are missing or API calls fail
    """
    chosen = (engine or os.environ.get("HUMANIZER_ENGINE") or "gemini").lower()
    return humanize_text_with_engine(text, chosen)


def humanize_text_with_engine(text: str, engine: str) -> str:
    """
    Route to the appropriate LLM engine with intelligent chunking.
    Strict LLM-only pipeline - all humanization via API.
    
    Args:
        text: The text to humanize
        engine: Engine to use ('deepseek', 'claude', or 'openai')
        
    Returns:
        Humanized text from the selected engine
        
    Raises:
        ValueError: If engine is not recognized
        RuntimeError: If API calls fail
    """
    engine = engine.lower()
    
    # Count words to determine if chunking is needed
    word_count = len(text.split())
    
    print(f"\n📊 TEXT ANALYSIS:")
    print(f"   Word count: {word_count}")
    print(f"   Chunking enabled: {CHUNKING_ENABLED}")
    print(f"   Chunking threshold: {CHUNKING_THRESHOLD}")
    print(f"   Will use chunking: {CHUNKING_ENABLED and word_count >= CHUNKING_THRESHOLD}")
    
    # If text is small or chunking is disabled, process directly
    if not CHUNKING_ENABLED or word_count < CHUNKING_THRESHOLD:
        print(f"   → Using direct processing (no chunking)")
        if engine == "openai":
            return humanize_with_openai(text)
        elif engine == "deepseek":
            return humanize_with_deepseek(text)
        elif engine == "claude":
            return humanize_with_claude(text)
        else:
            raise ValueError(f"Unknown engine: {engine}. Use 'deepseek', 'claude', or 'openai'")
    
    # Use chunking for large texts
    print(f"   → Using chunking pipeline")
    return humanize_with_chunking(text, engine)


def humanize_with_chunking(text: str, engine: str) -> str:
    """
    Humanize large text using intelligent chunking and rejoining.
    Optimized: 600-900 word chunks (2-3 chunks per 1500-2000 word essay).
    After rejoining, passes through ALTERNATIVE engine for final review.
    
    Args:
        text: The large text to humanize
        engine: Engine to use ('deepseek', 'claude', or 'openai')
        
    Returns:
        Seamlessly rejoined and reviewed humanized text
        
    Raises:
        RuntimeError: If chunking or processing fails
    """
    print(f"\n🔄 CHUNKING STARTED - Text length: {len(text)} chars, Engine: {engine}")
    print(f"   Using large chunks: {CHUNK_MIN_SIZE}-{CHUNK_MAX_SIZE} words per chunk (minimizes fragmentation)")
    
    # Initialize chunker and rejoiner with optimized settings
    chunker = TextChunker(
        min_chunk_size=CHUNK_MIN_SIZE,  # 500 words
        max_chunk_size=CHUNK_MAX_SIZE,   # 600 words
        overlap_sentences=2  # Keep 1-2 sentence overlap for continuity
    )
    rejoiner = TextRejoiner()
    
    # Split text into chunks
    chunks = chunker.chunk_text(text)
    chunk_count = len(chunks)
    print(f"✂️ Split into {chunk_count} chunks")
    
    # Process each chunk with dynamic temperature
    processed_chunks = []
    for chunk in chunks:
        print(f"  📝 Processing chunk {chunk.index + 1}/{chunk_count}")
        
        # Combine overlap with main text for context
        if chunk.has_overlap_start:
            chunk_input = f"{chunk.overlap_start}\n\n{chunk.text}"
        else:
            chunk_input = chunk.text
        
        # Humanize the chunk with chunk_index for temperature variation
        try:
            if engine == "deepseek":
                processed_text = humanize_with_deepseek(chunk_input, chunk.index)
            elif engine == "claude":
                processed_text = humanize_with_claude(chunk_input, chunk.index)
            elif engine == "openai":
                processed_text = humanize_with_openai(chunk_input, chunk.index)
            else:
                raise ValueError(f"Unknown engine: {engine}")
            
            print(f"  ✅ Chunk {chunk.index + 1} processed ({len(processed_text)} chars)")
            processed_chunks.append((chunk, processed_text))
            
        except Exception as e:
            print(f"  ⚠️ Chunk {chunk.index + 1} failed, retrying: {e}")
            # Retry once on failure
            try:
                if engine == "deepseek":
                    processed_text = humanize_with_deepseek(chunk_input, chunk.index)
                elif engine == "claude":
                    processed_text = humanize_with_claude(chunk_input, chunk.index)
                elif engine == "openai":
                    processed_text = humanize_with_openai(chunk_input, chunk.index)
                else:
                    raise ValueError(f"Unknown engine: {engine}")
                
                print(f"  ✅ Chunk {chunk.index + 1} retry successful")
                processed_chunks.append((chunk, processed_text))
            except Exception as retry_error:
                print(f"  ❌ Chunk {chunk.index + 1} failed permanently: {retry_error}")
                raise RuntimeError(f"Failed to process chunk {chunk.index}: {retry_error}")
    
    # Rejoin chunks
    print(f"🔗 Rejoining {len(processed_chunks)} chunks...")
    rejoined_text = rejoiner.rejoin_chunks(processed_chunks)
    print(f"✅ Chunks rejoined - Text: {len(rejoined_text)} chars")
    
    # FINAL REVIEW PASS - Use alternative engine to fix redundancies only
    alternative_engine = "openai" if engine == "gemini" else "gemini"
    print(f"\n🔍 FINAL REVIEW PASS - Using {alternative_engine.upper()} to fix redundancies...")
    print(f"   ⚠️ Review mode: ONLY fixing chunk boundaries and removing redundancies")
    print(f"   ⚠️ NOT rewriting content - surgical edits only")
    
    try:
        if alternative_engine == "gemini":
            gemini_engine = GeminiEngine()
            final_text = gemini_engine.final_review(rejoined_text, chunk_count)
        else:  # openai
            openai_engine = OpenAIEngine()
            final_text = openai_engine.final_review(rejoined_text, chunk_count)
        
        print(f"✅ Final review complete - Text: {len(final_text)} chars")
        
    except Exception as e:
        print(f"⚠️ Final review failed: {e}")
        print(f"   Returning rejoined text without review")
        final_text = rejoined_text
    
    print(f"✅ CHUNKING COMPLETE - Final text: {len(final_text)} chars\n")
    
    return final_text


def humanize_with_gemini(text: str, chunk_index: int = 0) -> str:
    """
    Humanize text using Google Gemini (OXO) with dynamic temperature.
    
    Args:
        text: The text to humanize
        chunk_index: Index of chunk for temperature variation
        
    Returns:
        Humanized text from Gemini
        
    Raises:
        RuntimeError: If GEMINI_API_KEY is not set or API fails
    """
    engine = GeminiEngine()
    return engine.humanize(text, chunk_index)


def humanize_with_openai(text: str, chunk_index: int = 0) -> str:
    """
    Humanize text using OpenAI (smurk) with dynamic temperature.
    
    Args:
        text: The text to humanize
        chunk_index: Index of chunk for temperature variation
        
    Returns:
        Humanized text from OpenAI
        
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API fails
    """
    engine = OpenAIEngine()
    return engine.humanize(text, chunk_index)


def humanize_with_claude(text: str, chunk_index: int = 0) -> str:
    """
    Humanize text using Claude (OXO) with dynamic temperature.
    
    Args:
        text: The text to humanize
        chunk_index: Index of chunk for temperature variation
        
    Returns:
        Humanized text from Claude
        
    Raises:
        RuntimeError: If ANTHROPIC_API_KEY is not set or API fails
    """
    # Use the Claude engine's humanize function
    chunks = [text]
    result = humanize_text_claude(chunks)
    return result[0] if result else text


def humanize_with_deepseek(text: str, chunk_index: int = 0) -> str:
    """
    Humanize text using DeepSeek (Loly) with dynamic temperature.
    
    Args:
        text: The text to humanize
        chunk_index: Index of chunk for temperature variation
        
    Returns:
        Humanized text from DeepSeek
        
    Raises:
        RuntimeError: If DEEPSEEK_API_KEY is not set or API fails
    """
    engine = DeepSeekEngine()
    return engine.humanize(text, chunk_index)
