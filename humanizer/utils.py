def humanize_with_claude(text: str, chunk_index: int = 0) -> str:
    """Humanize text using Claude engine."""
    return humanize_text_claude([text])[0]

def humanize_with_openai(text: str, chunk_index: int = 0) -> str:
    """Humanize text using OpenAI engine."""
    engine = OpenAIEngine()
    return engine.humanize(text, chunk_index)
"""
Text Humanization Utilities
Main interface for humanizing text using LLM engines.
Supports intelligent chunking for large texts.
"""

import os
from .llm_engines import GeminiEngine, OpenAIEngine, DeepSeekEngine
from .llm_engines.claude_engine import humanize_text_claude
from .chunking import TextChunker, TextRejoiner


# Chunking configuration (fixed 500 words per chunk, always enabled)
CHUNKING_ENABLED = True
CHUNK_MIN_SIZE = 500
CHUNK_MAX_SIZE = 500
CHUNKING_THRESHOLD = 500  # Always chunk at 500 words


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
    
    # Always use chunking, no preprocessing/analysis
    return humanize_with_chunking(text, engine)


def humanize_with_chunking(text: str, engine: str) -> str:
    # Humanize large text using chunking and rejoining. No preprocessing or final review.
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
    
                # Chunking only, no pre-processing or final review
                chunker = TextChunker(
                    min_chunk_size=CHUNK_MIN_SIZE,
                    max_chunk_size=CHUNK_MAX_SIZE,
                    overlap_sentences=2
                )
                rejoiner = TextRejoiner()
                chunks = chunker.chunk_text(text)
                processed_chunks = []
                for chunk in chunks:
                    chunk_input = f"{chunk.overlap_start}\n\n{chunk.text}" if chunk.has_overlap_start else chunk.text
                    if engine == "deepseek":
                        processed_text = humanize_with_deepseek(chunk_input, chunk.index)
                    elif engine == "claude":
                        processed_text = humanize_with_claude(chunk_input, chunk.index)
                    elif engine == "openai":
                        processed_text = humanize_with_openai(chunk_input, chunk.index)
                    else:
                        raise ValueError(f"Unknown engine: {engine}")
                    processed_chunks.append((chunk, processed_text))
                rejoined_text = rejoiner.rejoin_chunks(processed_chunks)


                return rejoined_text




def humanize_with_deepseek(text: str, chunk_index: int = 0) -> str:
    engine = DeepSeekEngine()
    return engine.humanize(text, chunk_index)
