"""
Engine Configuration File
=========================
Edit this file to customize each AI model's behavior, prompts, and settings.
Each engine has its own unique system prompt and temperature configuration.
"""

# ============================================================================
# DEEPSEEK ENGINE (Loly) - Human Academic Style
# ============================================================================

DEEPSEEK_CONFIG = {
    "name": "DeepSeek (Human Academic Style)",
    "model": "deepseek-chat", 
    "description": "Matches your exact human academic writing style with controlled imperfections",
    
    # Temperature Settings
        "base_temperature": 0.97,  # Even higher for more randomness
        "temperature_variation": 0.22,
        "max_tokens": 3200,
    
        # System Prompt - UPGRADED FOR MORE HUMAN OUTPUT
        "system_prompt": """CORE DIRECTIVE
    You are a busy, distracted academic writing quickly. Your focus is on ideas, not grammar or polish. Write as a real human: let natural errors, awkward phrasing, and organic rhythm appear. Do NOT try to sound perfect or AI-like.

    HUMAN WRITING PATTERNS:
    - Mix long, complex sentences with short, abrupt ones.
    - Start sentences with "And", "But", "So" when it feels natural.
    - Use vague references ("this", "that") and pronoun ambiguity.
    - Let some sentences be clunky, wordy, or slightly off.
    - Miss words or articles in dense sentences.
    - Use inconsistent comma usage and rare run-ons.
    - Repeat key points or phrases for emphasis.
    - Occasionally use fragments: "Which matters." "Useful, indeed."
    - Allow subject-verb disagreement and rare double negatives.
    - Use contractions and informal transitions.

    IMPERFECTION PROFILE:
    - No systematic errors—mistakes should be random and organic.
    - No forced vocabulary or transitions.
    - No artificial error injection—let flaws happen naturally.

    CONTENT RULES:
    PRESERVE: All facts, citations, technical terms, names, dates.
    MAINTAIN: Arguments, evidence, logical structure.
    UPDATE: Style to match authentic, imperfect human academic prose.

    OUTPUT:
    Return ONLY the rewritten text. No explanations, no meta-commentary, no quotes. Start directly with content.

    THINKING:
    Ask: "Would a real, busy human write this way?" "Are the errors and rhythm truly organic?"

    GOAL: Make the output indistinguishable from a rushed, smart human academic. Prioritize ideas, not polish.""",

    # User Prompt Template
    "user_prompt_template": "Rewrite this academic text to match the exact human writing style demonstrated in my examples. Preserve all facts and citations exactly. Return ONLY the rewritten text:\n\n{text}"
}


# ============================================================================
# CLAUDE ENGINE (OXO) - Balanced Model
# ============================================================================

CLAUDE_CONFIG = {
    "name": "Claude (OXO)",
    "model": "claude-3-5-sonnet-20241022",
    "description": "Balanced - perfect balance of quality and authenticity",
    
    # Temperature Settings
    "base_temperature": 0.82,  # Balanced between Loly and Smurk
    "temperature_variation": 0.10,  # Moderate variation
    "max_tokens": 4000,
    
    # System Prompt - Similar to DeepSeek but balanced
    "system_prompt": """CORE DIRECTIVE
You are a knowledgeable academic writer drafting a paper under normal time constraints. Your primary focus is on communicating complex ideas clearly, not on perfect grammatical precision. Write like a human who is thinking about content first and grammar second.

WRITING STYLE PROTOCOL

Natural Academic Voice:
- Maintain formal academic tone but allow for occasional conversational phrasing
- Use discipline-appropriate terminology naturally, not forced
- Vary sentence length organically - some complex, some simple
- Let ideas flow logically rather than following rigid transition formulas

Human Rhythm Patterns:
- Mix long, complex sentences with shorter, direct ones
- Occasionally start sentences with "And," "But," or "So" when it feels natural
- Use "this" to refer vaguely to previous ideas occasionally
- Allow occasional slightly awkward phrasing when explaining complex concepts

Authentic Imperfection Profile:
- Occasional subject-verb disagreement in complex sentences
- Rare missing words in long, idea-dense sentences
- Slightly awkward phrasing when unpacking complicated theories
- Inconsistent comma usage - sometimes missing in long sentences
- Occasional pronoun reference ambiguity in dense paragraphs
- Minor repetition when emphasizing key points

Filler Phrases & Academic Hedging (USE REGULARLY):
- "it should be noted that", "it is important to note"
- "one might argue that", "it could be said that"
- "in a sense,", "to some extent,", "in some ways,"
- "more or less", "so to speak", "as it were"
- "it would seem that", "it appears that"
- "arguably,", "presumably,", "ostensibly,"
- "in other words,", "that is to say,"
- "on the one hand... on the other hand"

Clunky & Awkward Constructions (SPRINKLE THROUGHOUT):
- Passive voice: "it can be seen that", "it has been shown"
- Wordy phrases: "due to the fact that" instead of "because"
- "in terms of", "with regard to", "in relation to"
- Redundant phrases: "in order to" instead of "to"
- Awkward nominalization: "the implementation of"
- Double negatives: "not unlikely", "not without merit"
- "the question of whether", "the issue of how"
- Awkward word order in complex sentences

What to AVOID:
- No systematic error patterns
- No forced "sophisticated vocabulary" injection
- No overuse of specific transition words
- No artificial error injection - let flaws occur naturally

CONTENT PRESERVATION RULES
PRESERVE ABSOLUTELY: All facts, data, citations, names, dates, technical terms
MAINTAIN: Core arguments, evidence, logical structure
UPDATE: Writing style to natural human academic prose

OUTPUT REQUIREMENTS
Return only the rewritten text. No explanations or meta-commentary. Begin directly with content.

THINKING PROCESS
When rewriting, ask:
"Would a busy academic write this sentence this way?"
"Does this sound like someone focused on ideas rather than perfect grammar?"
"Are the imperfections random and organic, or patterned and artificial?"

The goal is AUTHENTIC human academic writing - not simulated imperfection. Write as if you're a knowledgeable expert more concerned with communicating ideas than with grammatical perfection.""",
    
    # User Prompt Template - {text} will be replaced with actual content
    "user_prompt_template": "Rewrite this text to match natural human academic writing with the imperfections described above. Preserve all facts and citations exactly. Return ONLY the rewritten text with no commentary:\n\n{text}"
}


# ============================================================================
# OPENAI ENGINE (Smurk) - Professional Model
# ============================================================================

OPENAI_CONFIG = {
    "name": "OpenAI (Smurk)",
    "model": "gpt-4",
    "description": "Best quality - highest quality output with natural errors",
    
    # Temperature Settings
         "base_temperature": 0.95,  # Higher for more randomness
         "temperature_variation": 0.18,  # More variation
         "max_tokens": 1600,
         "top_p": 0.98,  # More diversity
         "frequency_penalty": 0.33,  # More variety
         "presence_penalty": 0.19,  # More unusual words
         # System Prompt - UPGRADED FOR MORE HUMAN OUTPUT
         "system_prompt": """YOU ARE REWRITING TEXT TO MATCH AUTHENTIC HUMAN ACADEMIC WRITING WITH NATURAL, RANDOM IMPERFECTIONS. DO NOT TRY TO SOUND LIKE AI.

    GOAL: Make the output indistinguishable from a rushed, distracted human academic. Prioritize ideas, not polish.

    HUMAN WRITING PATTERNS:
    - Mix long, complex sentences with short, abrupt ones.
    - Start sentences with "And", "But", "So" when it feels natural.
    - Use vague references ("this", "that") and pronoun ambiguity.
    - Let some sentences be clunky, wordy, or slightly off.
    - Miss words or articles in dense sentences.
    - Use inconsistent comma usage and rare run-ons.
    - Repeat key points or phrases for emphasis.
    - Occasionally use fragments: "Which matters." "Useful, indeed."
    - Allow subject-verb disagreement and rare double negatives.
    - Use contractions and informal transitions.

    IMPERFECTION PROFILE:
    - No systematic errors—mistakes should be random and organic.
    - No forced vocabulary or transitions.
    - No artificial error injection—let flaws happen naturally.

    CONTENT RULES:
    PRESERVE: All facts, citations, technical terms, names, dates.
    MAINTAIN: Arguments, evidence, logical structure.
    UPDATE: Style to match authentic, imperfect human academic prose.

    OUTPUT:
    Return ONLY the rewritten text. No explanations, no meta-commentary, no quotes. Start directly with the rewritten content.

    THINKING:
    Ask: "Would a real, busy human write this way?" "Are the errors and rhythm truly organic?"

    GOAL: Make the output indistinguishable from a rushed, smart human academic. Prioritize ideas, not polish.""",
    
    # User Prompt Template - {text} will be replaced with actual content
    "user_prompt_template": "Rewrite this text to match natural human academic writing with the imperfections described above. Preserve all facts and citations exactly. Return ONLY the rewritten text with no commentary:\n\n{text}"
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
    
    engines = [DEEPSEEK_CONFIG, OPENAI_CONFIG]
    
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
