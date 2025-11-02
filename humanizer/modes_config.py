"""
Humanization Modes Configuration
=================================
Defines 6 modes for text humanization with different styles and temperatures.
"""

# Model identifier
MODEL_ID = "ft:gpt-4.1-mini-2025-04-14:valdace-ai:humanizerb0:CXCYIoX9"

# ============================================================================
# MODE DEFINITIONS
# ============================================================================

MODES = {
    "recommended": {
        "name": "Recommended",
        "description": "⭐ Best for AI detection evasion - Optimized settings for natural output",
        "temperature": 0.2,
        "use_prompt": False,  # No additional prompt instructions
        "badge": "RECOMMENDED",
        "badge_color": "#28a745"
    },
    
    "readability": {
        "name": "Readability",
        "description": "Clear and easy to understand - Perfect for general audiences",
        "temperature": 0.3,
        "use_prompt": True,
        "prompt": """Transform this text to be highly readable and accessible:

- Use clear, straightforward language
- Keep sentences short and easy to follow
- Maintain a natural flow that anyone can understand
- Include subtle variations that feel human
- Preserve all key information

Text to transform:
{text}""",
        "badge": None,
        "badge_color": None
    },
    
    "formal": {
        "name": "Formal",
        "description": "Professional and academic tone",
        "temperature": 0.4,
        "use_prompt": True,
        "prompt": """Transform this text to match a formal academic writing style while maintaining authenticity:

- Use sophisticated vocabulary and complex sentence structures
- Maintain professional tone throughout
- Include subtle grammatical variations that humans make
- Preserve all facts and citations
- Avoid overly polished or perfect phrasing

Text to transform:
{text}""",
        "badge": None,
        "badge_color": None
    },
    
    "conversational": {
        "name": "Conversational",
        "description": "Natural, everyday speaking style",
        "temperature": 0.7,
        "use_prompt": True,
        "prompt": """Rewrite this text in a natural, conversational tone:

- Use everyday language and casual phrasing
- Include contractions where natural
- Vary sentence length for natural flow
- Add subtle imperfections typical of casual speech
- Keep the meaning intact

Text to transform:
{text}""",
        "badge": None,
        "badge_color": None
    },
    
    "informal": {
        "name": "Informal",
        "description": "Relaxed and approachable tone",
        "temperature": 0.8,
        "use_prompt": True,
        "prompt": """Rewrite this text in an informal, friendly style:

- Use simple, accessible language
- Keep sentences short and punchy
- Add personality and warmth
- Include natural human writing patterns
- Make it feel genuine and unpolished

Text to transform:
{text}""",
        "badge": None,
        "badge_color": None
    },
    
    "academic": {
        "name": "Academic",
        "description": "Scholarly writing with analytical depth",
        "temperature": 0.5,
        "use_prompt": True,
        "prompt": """Transform this text into scholarly academic writing:

- Use advanced academic vocabulary
- Employ complex, analytical sentence structures
- Include hedging and qualification where appropriate
- Maintain rigorous intellectual tone
- Add subtle authentic academic writing patterns
- Preserve all citations and references

Text to transform:
{text}""",
        "badge": None,
        "badge_color": None
    }
}

# Default mode
DEFAULT_MODE = "recommended"


def get_mode_config(mode_name: str) -> dict:
    """
    Get configuration for a specific mode.
    
    Args:
        mode_name: Name of the mode (recommended, formal, conversational, informal, academic)
        
    Returns:
        Mode configuration dictionary
        
    Raises:
        ValueError: If mode name is not recognized
    """
    mode_name = mode_name.lower()
    
    if mode_name not in MODES:
        raise ValueError(f"Unknown mode: {mode_name}. Valid options: {', '.join(MODES.keys())}")
    
    return MODES[mode_name]


def get_all_modes():
    """Return list of all available modes with metadata."""
    return [
        {
            "id": mode_id,
            **config
        }
        for mode_id, config in MODES.items()
    ]


def format_prompt_for_mode(mode_name: str, text: str) -> str:
    """
    Format the prompt for a specific mode.
    
    Args:
        mode_name: Name of the mode
        text: Text to be humanized
        
    Returns:
        Formatted prompt string or None if mode doesn't use prompts
    """
    config = get_mode_config(mode_name)
    
    if not config["use_prompt"]:
        return None
    
    return config["prompt"].format(text=text)
