from .prompts import COMPREHENSIVE_TRANSFORMATION_PROMPT

COMPREHENSIVE_SYSTEM_PROMPT = (
    "You are a Text Style Transformation Engine that must execute the Comprehensive Transformation Prompt exactly as provided in the user message. "
    "Follow every mandatory synonym replacement, phrase unpacking requirement, sentence restructuring rule, and tonal constraint mechanically, "
    "and return only the transformed text."
)

# ============================================================================
# PROFESSIONAL HUMANIZATION PROTOCOL - Academic-to-Professional Transformation
# ============================================================================

PROFESSIONAL_HUMANIZER_CONFIG = {
    "name": "Professional Humanizer (Academic-to-Professional)",
    "model": "gpt-4-pro-humanizer",
    "description": "Transforms academic essays into persuasive, professional articles with elevated readability and authority.",
    "base_temperature": 0.92,
    "temperature_variation": 0.15,
    "max_tokens": 2400,
    "system_prompt": COMPREHENSIVE_SYSTEM_PROMPT,
    "user_prompt_template": COMPREHENSIVE_TRANSFORMATION_PROMPT,
}

# ============================================================================
# DEEPSEEK ENGINE (Loly) - Human Academic Style
# ============================================================================

DEEPSEEK_CONFIG = {
    "name": "DeepSeek (Human Academic Style)",
    "model": "deepseek-chat",
    "description": "Matches your exact human academic writing style with controlled imperfections",
    "base_temperature": 0.97,
    "temperature_variation": 0.22,
    "max_tokens": 3200,
    "system_prompt": COMPREHENSIVE_SYSTEM_PROMPT,
    "user_prompt_template": COMPREHENSIVE_TRANSFORMATION_PROMPT,
}

# ============================================================================
# CLAUDE ENGINE (OXO) - Balanced Model
# ============================================================================

CLAUDE_CONFIG = {
    "name": "Claude (OXO)",
    "model": "claude-3.7",
    "description": "Balanced - perfect balance of quality and authenticity",
    "base_temperature": 0.82,
    "temperature_variation": 0.10,
    "max_tokens": 4000,
    "system_prompt": COMPREHENSIVE_SYSTEM_PROMPT,
    "user_prompt_template": COMPREHENSIVE_TRANSFORMATION_PROMPT,
}

# ============================================================================
# OPENAI ENGINE (Smurk) - Professional Model
# ============================================================================

OPENAI_CONFIG = {
    "name": "OpenAI (Smurk)",
    "model": "gpt-4.1",
    "description": "Best quality - highest quality output with natural errors",
    "base_temperature": 0.95,
    "temperature_variation": 0.18,
    "max_tokens": 1600,
    "top_p": 0.98,
    "frequency_penalty": 0.33,
    "presence_penalty": 0.19,
    "system_prompt": COMPREHENSIVE_SYSTEM_PROMPT,
    "user_prompt_template": COMPREHENSIVE_TRANSFORMATION_PROMPT,
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
    elif engine_name in ("claude", "anthropic", "oxo"):
        return CLAUDE_CONFIG
    elif engine_name in ("openai", "gpt", "chatgpt"):
        return OPENAI_CONFIG
    elif engine_name in ("professional", "pro-humanizer", "gpt-4-pro-humanizer"):
        return PROFESSIONAL_HUMANIZER_CONFIG
    else:
        raise ValueError(f"Unknown engine: {engine_name}. Valid options: 'deepseek', 'claude', 'openai', 'professional'")


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
    
    engines = [DEEPSEEK_CONFIG, CLAUDE_CONFIG, OPENAI_CONFIG, PROFESSIONAL_HUMANIZER_CONFIG]
    for config in engines:
        print(f"\n{config['name']}")
        print(f"  Model: {config['model']}")
        print(f"  Description: {config['description']}")
        print(f"  Base Temperature: {config['base_temperature']}")
        print(f"  Temperature Variation: {config['temperature_variation']}")
        print(f"  Max Tokens: {config['max_tokens']}")
    
    print("\n" + "=" * 80)
    print("TO CUSTOMIZE:")
    print("  Edit humanizer/engine_config.py to change prompts and settings")
    print("=" * 80)


if __name__ == "__main__":
    list_available_engines()
