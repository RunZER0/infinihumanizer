"""
Direct Command Prompts for AI Humanization Engines.
Each prompt is designed to command directly without room for interpretation
and beat AI detectors by understanding their detection methods.

INTENSITY LEVELS:
- STANDARD: Balanced humanization (deepseek, chatgpt prompts)
- NUCLEAR: Maximum evasion through deliberate imperfection injection
"""

# Import nuclear mode
from humanizer.nuclear_mode import get_nuclear_prompt, NUCLEAR_TURNITIN_BREAKER

# ============================================================================
# COMPREHENSIVE TRANSFORMATION PROTOCOL PROMPT
# ============================================================================

COMPREHENSIVE_TRANSFORMATION_PROMPT = """Comprehensive Transformation Prompt
You are now a Text Style Transformation Engine. Your operation is governed by a strict protocol. You do not improvise, interpret, or "improve" text. You execute a series of stylistic rules mechanically.

CORE DIRECTIVE: Transform the input text into a formally distinct version by systematically applying the rules below. The output must sound like a dry, academic paraphrase. It must be recognizably different from the original in style, yet retain all factual content, structure, and citations. Slight awkwardness or a loss of elegance is not only acceptable but often expected.

NON-NEGOTIABLE STYLISTIC RULES:

SYNONYM REPLACEMENT: You MUST swap the following words/phrases exactly as instructed. This is not a suggestion.

shows → demonstrates

explains / explores → addresses / seeks to answer

uses → employs / leverages

provides → offers / can serve as the source of

foundational → primary

possesses → has

unique → special

profound → deep

crucial → essential / critical

enhances → improves

plays a central role / is central → is at the center stage

for example → as one example

similarly → equally

however → but / nevertheless

therefore / thus → this means that / which is why

PHRASE UNPACKING: You MUST dismantle concise phrasing and make it more wordy and explicit.

INPUT: provides essential data

OUTPUT: can serve as the source of the necessary data

INPUT: through a process

OUTPUT: it was a process in which

INPUT: to enhance performance

OUTPUT: in order to achieve an improvement in performance

SENTENCE RESTRUCTURING: You MUST alter the sentence flow away from direct, active declarations.

Prefer sentences that start with "Since...", "To...", or "In order to...".

Shift from active to more passive or abstract constructions.

INPUT: My research involved examining articles.

OUTPUT: The research process entailed the review of scholarly articles.

TONE ENFORCEMENT: The final output MUST be formal and academic. You MUST strip out any conversational flair, rhetorical questions, or punchy language. The result should be functionally formal, not elegantly written.

TRANSFORMATION EXAMPLES - MIMIC THIS STYLE EXACTLY:

Original: "His best move is connecting street-level life to national party building."

Target: "His greatest step is to relate the life of the streets to national party building."

Original: "This source is foundational to my project, offering a specific, data-backed example."

Target: "This source is a primary source in my project as it provides a particular, factual representation..."

Original: "Roediger persuasively shows that Irish workers became 'white workers' through a mutually reinforcing process."

Target: "Roediger effectively demonstrates that it was a mutually reinforcing process in which the Irish workers gradually came to be known as white workers."

YOUR TASK:
Apply these rules MECHANICALLY to the following text. Do not deviate. Your sole purpose is to output a transformed version that rigidly adheres to this protocol.

TEXT TO TRANSFORM:

{text}
"""

# Shared prompt bindings for all supported engines
DEEPSEEK_PROMPT = COMPREHENSIVE_TRANSFORMATION_PROMPT
CLAUDE_PROMPT = COMPREHENSIVE_TRANSFORMATION_PROMPT

# ============================================================================
# OPENAI (CHATGPT) PROMPT ALIAS
# ============================================================================

CHATGPT_PROMPT = COMPREHENSIVE_TRANSFORMATION_PROMPT
# ============================================================================
# UNIVERSAL HUMANIZATION RULES (Supplement for any prompt)
# ============================================================================

UNIVERSAL_HUMANIZATION_RULES = """
## ADD THESE TO ANY PROMPT AS NEEDED:

**IMMEDIATE IMPERFECTION COMMANDS:**
1. CHANGE 30% OF SENTENCE STRUCTURES TO BE LESS PERFECT
2. INTRODUCE 15% UNEXPECTED BUT APPROPRIATE WORD CHOICES
**MANDATORY IMPERFECTION INJECTION:**
1. **FORCE 10-15% GRAMMATICAL IMPERFECTIONS** (comma splices, fragments, awkward constructions)
2. BREAK 30% OF PARALLEL STRUCTURES  
3. **CREATE 12-15% ASYMMETRICAL OR SLIGHTLY AWKWARD PHRASING**
4. **ADD 8-12% SENTENCE FRAGMENTS FOR RHYTHMIC VARIATION**
5. USE HEDGING LANGUAGE IN 20% OF ASSERTIONS
6. **CRITICAL: Include self-corrections and false starts (5-8%)**

**DETECTION BEATING TECHNIQUES:**
- **INJECT AUTHENTIC HUMAN ERRORS - NON-NEGOTIABLE**
- VARY PERPLEXITY THROUGH SURPRISING WORD COMBINATIONS
- INCREASE BURSTINESS THROUGH EXTREME LENGTH VARIATION
- BREAK CONSISTENT TRANSITION PATTERNS
- ADD HUMAN COGNITIVE PATTERNS (MEMORY, ASSOCIATION, HEDGING, ERRORS)

**PRESERVATION ABSOLUTES:**
- TECHNICAL TERMS: NEVER CHANGE
- PROPER NOUNS: NEVER CHANGE  
- NUMBERS/DATES: NEVER CHANGE
- CORE ARGUMENT: PRESERVE EXACTLY
- DOMAIN KNOWLEDGE: MAINTAIN ACCURACY

**REMINDER: Text must have natural imperfections. Perfect grammar = AI detection.**
"""

# ============================================================================
# ENHANCED PROMPTS WITH PREPROCESSING INTEGRATION
# ============================================================================

def build_enhanced_prompt(base_prompt: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Build enhanced prompt with preprocessing analysis integration
    
    Args:
        base_prompt: Base prompt template (DEEPSEEK_PROMPT, GEMINI_PROMPT, or CHATGPT_PROMPT)
        text: Text to humanize
        preprocessing_analysis: Optional analysis from TextPreprocessor
    
    Returns:
        Enhanced prompt with preservation rules and targeted instructions
    """
    prompt = base_prompt.format(text=text)
    
    if preprocessing_analysis:
        # Add preservation rules from preprocessing
        preservation_map = preprocessing_analysis.get('preservation_map', {})
        guidelines = preprocessing_analysis.get('humanization_guidelines', {})
        
        preservation_section = "\n## ADDITIONAL PRESERVATION RULES FROM ANALYSIS:\n"
        
        if preservation_map.get('technical_terms'):
            terms = ', '.join(list(preservation_map['technical_terms'])[:10])
            preservation_section += f"- PRESERVE THESE TECHNICAL TERMS: {terms}\n"
        
        if preservation_map.get('proper_nouns'):
            nouns = ', '.join(list(preservation_map['proper_nouns'])[:10])
            preservation_section += f"- NEVER CHANGE THESE PROPER NOUNS: {nouns}\n"
        
        if preservation_map.get('numbers_dates'):
            nums = ', '.join(preservation_map['numbers_dates'][:5])
            preservation_section += f"- MAINTAIN THESE EXACT VALUES: {nums}\n"
        
        # Add targeted recommendations
        if guidelines.get('variation_recommendations'):
            preservation_section += "\n## PRIORITY HUMANIZATION TARGETS:\n"
            for rec in guidelines['variation_recommendations'][:5]:
                preservation_section += f"- {rec.upper()}\n"
        
        # Insert before the text to transform
        prompt = prompt.replace("## TEXT TO TRANSFORM:", 
                              preservation_section + "\n## TEXT TO TRANSFORM:")
        prompt = prompt.replace("## INPUT TEXT:", 
                              preservation_section + "\n## INPUT TEXT:")
        prompt = prompt.replace("## TEXT TO HUMANIZE:", 
                              preservation_section + "\n## TEXT TO HUMANIZE:")
    
    return prompt


def get_prompt_by_engine(engine_name: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Get the appropriate prompt for a specific engine
    
    Args:
        engine_name: 'deepseek', 'chatgpt'/'openai', or 'nuclear' (⚛️ MAXIMUM EVASION)
        text: Text to humanize
        preprocessing_analysis: Optional analysis from TextPreprocessor
    
    Returns:
        Formatted prompt ready for the engine
    """
    engine_map = {
        'deepseek': DEEPSEEK_PROMPT,
        'chatgpt': CHATGPT_PROMPT,
        'openai': CHATGPT_PROMPT,
        'gpt': CHATGPT_PROMPT,
        'nuclear': NUCLEAR_TURNITIN_BREAKER  # ⚛️ THE NUCLEAR OPTION
    }
    
    base_prompt = engine_map.get(engine_name.lower(), CHATGPT_PROMPT)
    
    # Nuclear mode uses its own prompt directly, no enhancement needed
    if engine_name.lower() == 'nuclear':
        return base_prompt.format(text=text)
    
    return build_enhanced_prompt(base_prompt, text, preprocessing_analysis)


def get_intensity_adjusted_prompt(base_prompt: str, text: str, intensity: float) -> str:
    """
    Adjust prompt aggressiveness based on intensity level
    
    Args:
        base_prompt: Base prompt template
        text: Text to humanize
        intensity: Float from 0.0 to 1.0 (how aggressive to humanize)
    
    Returns:
        Intensity-adjusted prompt
    """
    prompt = base_prompt.format(text=text)
    
    # Add intensity modifier
    if intensity > 0.7:
        modifier = """
## INTENSITY LEVEL: MAXIMUM
- APPLY ALL HUMANIZATION TECHNIQUES AT FULL STRENGTH
- MAXIMIZE SENTENCE VARIATION AND IMPERFECTIONS
- AGGRESSIVE BURSTINESS AND PERPLEXITY INJECTION
"""
    elif intensity > 0.4:
        modifier = """
## INTENSITY LEVEL: MODERATE
- APPLY HUMANIZATION TECHNIQUES AT BALANCED LEVEL
- MODERATE SENTENCE VARIATION
- STANDARD BURSTINESS AND PERPLEXITY
"""
    else:
        modifier = """
## INTENSITY LEVEL: MINIMAL
- APPLY HUMANIZATION TECHNIQUES CONSERVATIVELY
- SUBTLE SENTENCE VARIATION ONLY
- LIGHT TOUCH ON PERPLEXITY AND BURSTINESS
- PRESERVE MAXIMUM PROFESSIONAL FORMALITY
"""
    
    # Insert intensity modifier after mission statement
    prompt = prompt.replace("# MISSION:", modifier + "\n# MISSION:")
    prompt = prompt.replace("# COMMAND:", modifier + "\n# COMMAND:")
    prompt = prompt.replace("# DIRECT COMMANDS:", modifier + "\n# DIRECT COMMANDS:")
    
    return prompt


# ============================================================================
# PROMPT TEMPLATES SUMMARY
# ============================================================================

PROMPT_SUMMARY = {
    'deepseek': {
        'name': 'The Imperfection Specialist',
        'strength': 'Maximum imperfection injection',
        'best_for': 'Aggressive humanization, beating strict detectors',
        'intensity': 'High',
        'focus': 'Cognitive patterns, natural flaws, structural imperfections'
    },
    'chatgpt': {
        'name': 'The Perfection Breaker',
        'strength': 'Quality-preserving humanization',
        'best_for': 'Professional content, balanced humanization',
        'intensity': 'Medium',
        'focus': 'Breaking AI perfection while maintaining quality'
    },
    'nuclear': {
        'name': '⚛️ The Nuclear Option',
        'strength': 'MAXIMUM evasion through deliberate imperfection',
        'best_for': 'CRITICAL detection risk, Turnitin/GPTZero evasion',
        'intensity': 'EXTREME (95%+ evasion)',
        'focus': 'Error injection, cognitive imperfections, chaos patterns'
    }
}


def print_prompt_info():
    """Print information about available prompts"""
    print("=" * 80)
    print("AI HUMANIZATION PROMPT ENGINES")
    print("=" * 80)
    
    for engine, info in PROMPT_SUMMARY.items():
        print(f"\n{engine.upper()}: {info['name']}")
        print(f"  Strength: {info['strength']}")
        print(f"  Best for: {info['best_for']}")
        print(f"  Intensity: {info['intensity']}")
        print(f"  Focus: {info['focus']}")
    
    print("\n" + "=" * 80)
    print("USAGE:")
    print("  from humanizer.prompts import get_prompt_by_engine")
    print("  prompt = get_prompt_by_engine('deepseek', your_text)")
    print("=" * 80)


if __name__ == "__main__":
    print_prompt_info()
    
    # Demo
    sample_text = "Artificial intelligence has revolutionized numerous industries."
    print("\n\nDEMO - DeepSeek Prompt Preview:")
    print("-" * 80)
    prompt = get_prompt_by_engine('deepseek', sample_text)
    print(prompt[:500] + "...")
