"""
Humanization Modes Configuration
=================================
Defines 6 modes for text humanization with different styles and temperatures.
Supports multiple fine-tuned models for quality selection.
"""

# ============================================================================
# SYSTEM PROMPTS — defined first so AVAILABLE_MODELS can reference them
# ============================================================================

SYSTEM_PROMPT_KAZE = "You are a humanizer. Rewrite the user's text so it sounds naturally written by a human while preserving the original meaning, argument, quotations, citations, and technical accuracy. Remove robotic phrasing, generic transitions, inflated wording, and overly uniform sentence rhythm. Do not add new ideas, examples, or claims. Do not change citation text or quoted wording. Return only the rewritten text."

SYSTEM_PROMPT_NAMI = "You are a humanizer. You must always rewrite the provided text to sound like a natural human. Never return the same text as the input. Your goal is to transform the structure, rhythm, and vocabulary while preserving meaning, citations, and quotes."

# Legacy alias used by mode configs
SYSTEM_PROMPT = SYSTEM_PROMPT_KAZE

# ============================================================================
# MODEL SELECTION
# ============================================================================

AVAILABLE_MODELS = {
    # ── Kaze tier (hope run) ──────────────────────────────
    "kaze-i": {
        "id": "ft:gpt-4.1-mini-2025-04-14:ynai:hope:DNYCXWru:ckpt-step-412",
        "name": "Kaze-I",
        "description": "Early checkpoint",
        "system_prompt": SYSTEM_PROMPT_KAZE,
        "badge": None
    },
    "kaze-ii": {
        "id": "ft:gpt-4.1-mini-2025-04-14:ynai:hope:DNYCYreS:ckpt-step-824",
        "name": "Kaze-II",
        "description": "Late checkpoint",
        "system_prompt": SYSTEM_PROMPT_KAZE,
        "badge": None
    },
    "kaze": {
        "id": "ft:gpt-4.1-mini-2025-04-14:ynai:hope:DNYCY1OJ",
        "name": "Kaze",
        "description": "Final — best of Kaze tier",
        "system_prompt": SYSTEM_PROMPT_KAZE,
        "badge": None
    },
    # ── Nami tier — premium (hopetoo run) ────────────────
    "nami-i": {
        "id": "ft:gpt-4.1-mini-2025-04-14:ynai:hopetoo:DNkpWxS4:ckpt-step-323",
        "name": "Nami-I",
        "description": "Early checkpoint",
        "system_prompt": SYSTEM_PROMPT_NAMI,
        "badge": "PREMIUM"
    },
}

# Default model
DEFAULT_MODEL = "nami-i"
MODEL_ID = AVAILABLE_MODELS[DEFAULT_MODEL]["id"]

# ============================================================================
# MODE DEFINITIONS
# ============================================================================

MODES = {
    "recommended": {
        "name": "Recommended",
        "description": "Optimized settings for natural, human-like output",
        "temperature": 0.7,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
        "badge": "RECOMMENDED",
        "badge_color": "#28a745"
    },
    
    "readability": {
        "name": "Readability",
        "description": "Clear and accessible writing style",
        "temperature": 0.65,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
        "badge": None,
        "badge_color": None
    },
    
    "formal": {
        "name": "Formal",
        "description": "Professional academic tone",
        "temperature": 0.6,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
        "badge": None,
        "badge_color": None
    },
    
    "conversational": {
        "name": "Conversational",
        "description": "Natural everyday speaking style",
        "temperature": 0.75,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
        "badge": None,
        "badge_color": None
    },
    
    "informal": {
        "name": "Informal",
        "description": "Relaxed and approachable tone",
        "temperature": 0.8,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
        "badge": None,
        "badge_color": None
    },
    
    "academic": {
        "name": "Academic",
        "description": "Scholarly writing with depth",
        "temperature": 0.65,
        "system_prompt": SYSTEM_PROMPT,
        "prompt": "{text}",
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


def get_system_prompt_for_mode(mode_name: str) -> str:
    """
    Get the system prompt for a specific mode.
    All modes use the same system prompt matching the fine-tuned model's training data.
    """
    config = get_mode_config(mode_name)
    return config.get("system_prompt", SYSTEM_PROMPT)


def format_prompt_for_mode(mode_name: str, text: str) -> str:
    """
    Format the user message prompt for a specific mode.
    Every mode has a prompt; returns it formatted with the given text.
    """
    config = get_mode_config(mode_name)
    return config["prompt"].format(text=text)


def get_all_models():
    """Get all available models as a list of dicts"""
    return [
        {
            "id": model_id,
            "name": config["name"],
            "description": config["description"],
            "badge": config.get("badge"),
            "model_id": config["id"]
        }
        for model_id, config in AVAILABLE_MODELS.items()
    ]


def get_model_id(model_key: str = None) -> str:
    """Get the actual model ID for a given model key"""
    if not model_key or model_key not in AVAILABLE_MODELS:
        model_key = DEFAULT_MODEL
    return AVAILABLE_MODELS[model_key]["id"]


def get_model_system_prompt(model_key: str = None) -> str:
    """Get the system prompt for a given model key"""
    if not model_key or model_key not in AVAILABLE_MODELS:
        model_key = DEFAULT_MODEL
    return AVAILABLE_MODELS[model_key]["system_prompt"]
