"""
Engine Configuration File - UPDATED
=========================
Each engine uses its own optimized humanization prompt from prompts.py
"""

from .prompts import DEEPSEEK_PROMPT, CLAUDE_PROMPT, OPENAI_PROMPT

# ============================================================================
# DEEPSEEK ENGINE CONFIGURATION
# ============================================================================

DEEPSEEK_CONFIG = {
    "name": "DeepSeek Human Paraphraser",
    "model": "deepseek-chat", 
    "description": "Natural text paraphrasing with human imperfections",
    
    "base_temperature": 0.3,
    "temperature_variation": 0.1,
    "max_tokens": 4000,
    
    "system_prompt": "You are a text paraphraser who transforms AI-generated text into human-sounding output.",
    "user_prompt_template": DEEPSEEK_PROMPT
}

# ============================================================================
# CLAUDE ENGINE CONFIGURATION
# ============================================================================

CLAUDE_CONFIG = {
    "name": "Claude Human Paraphraser",
    "model": "claude-3-7-sonnet-20250219",
    "description": "Natural text paraphrasing with human imperfections",
    
    "base_temperature": 0.3,
    "temperature_variation": 0.15,
    "max_tokens": 8192,
    
    "system_prompt": "You are a text paraphraser who transforms AI-generated text into human-sounding output.",
    "user_prompt_template": CLAUDE_PROMPT
}

# ============================================================================
# OPENAI ENGINE CONFIGURATION
# ============================================================================

OPENAI_CONFIG = {
    "name": "OpenAI Human Paraphraser",
    "model": "gpt-4-turbo-preview",
    "description": "Natural text paraphrasing with human imperfections",
    
    "base_temperature": 0.3,
    "temperature_variation": 0.1,
    "max_tokens": 4000,
    "top_p": 0.9,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.2,
    
    "system_prompt": "You are a text paraphraser who transforms AI-generated text into human-sounding output.",
    "user_prompt_template": OPENAI_PROMPT
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_engine_config(engine_name: str) -> dict:
    """
    Get configuration for a specific engine.
    
    Args:
        engine_name: 'deepseek', 'claude', or 'openai'
        
    Returns:
        Configuration dictionary for the engine
        
    Raises:
        ValueError: If engine name is not recognized
    """
    engine_name = engine_name.lower()
    
    if engine_name == "deepseek":
        return DEEPSEEK_CONFIG
    elif engine_name in ("claude", "anthropic"):
        return CLAUDE_CONFIG
    elif engine_name in ("openai", "gpt"):
        return OPENAI_CONFIG
    else:
        raise ValueError(f"Unknown engine: {engine_name}. Valid options: 'deepseek', 'claude', 'openai'")


def calculate_temperature(base_temp: float, variation: float, chunk_index: int) -> float:
    """
    Calculate dynamic temperature based on chunk index.
    
    Args:
        base_temp: Base temperature value
        variation: How much to vary temperature
        chunk_index: Index of current chunk
        
    Returns:
        Temperature value for this chunk
    """
    # Vary temperature based on chunk index (cycles through 4 values)
    temp_offset = (chunk_index % 4) * (variation / 4)
    return min(1.0, base_temp + temp_offset)


def list_available_engines():
    """Print information about available engines."""
    print("=" * 80)
    print("AVAILABLE HUMANIZATION ENGINES")
    print("=" * 80)
    
    engines = [DEEPSEEK_CONFIG, CLAUDE_CONFIG, OPENAI_CONFIG]
    for config in engines:
        print(f"\n{config['name']}")
        print(f"  Model: {config['model']}")
        print(f"  Description: {config['description']}")
        print(f"  Base Temperature: {config['base_temperature']}")
        print(f"  Temperature Variation: {config['temperature_variation']}")
        print(f"  Max Tokens: {config['max_tokens']}")
    
    print("\n" + "=" * 80)
    print("APPROACH: Natural text paraphrasing with human imperfections")
    print("=" * 80)


if __name__ == "__main__":
    list_available_engines()

