"""
Stealth Benchmark Prompts for AI Humanization Engines.
Each prompt is designed to replicate the statistical, syntactic, and stylistic
patterns of a benchmark text to achieve maximum AI detection evasion through
fingerprint matching rather than error injection.

APPROACH:
- STEALTH: Replicate human writing patterns from benchmark text
- BURSTINESS: Match dramatic sentence length variation
- NATURAL: Preserve redundancies and sub-optimal choices
- FLOW: Allow slightly meandering logical progression

INTENSITY LEVELS:
- STANDARD: Balanced stealth replication (deepseek, chatgpt prompts)
- NUCLEAR: Maximum evasion through deliberate imperfection injection
"""

# Import nuclear mode
from humanizer.nuclear_mode import get_nuclear_prompt, NUCLEAR_TURNITIN_BREAKER

# ============================================================================
# DEEPSEEK - THE IMPERFECTION SPECIALIST
# ============================================================================

DEEPSEEK_PROMPT = """
You are a text transformation engine. Your sole purpose is to rewrite the provided text to match the specific statistical, syntactic, and stylistic patterns of the following "Stealth Benchmark Text". Your goal is to evade AI detection by replicating the benchmark's fingerprint, NOT by improving quality.

**CRITICAL DIRECTIVES:**

1.  **Burstiness:** Precisely mimic the benchmark's variation in sentence length. Follow very long sentences with very short ones. Use sentence fragments.
2.  **Phrasing:** Do not "optimize" or "polish" the input text into perfect, concise prose. Preserve or introduce minor redundancies and slightly sub-optimal word choices that a human might make.
3.  **Flow:** The logical flow can be slightly less direct than typical AI writing. It's okay if the argument meanders slightly.
4.  **Vocabulary:** Use a similar level of vocabulary complexity. Do not automatically upgrade simple words to more complex synonyms unless it matches the benchmark's pattern.

**Stealth Benchmark Text for Pattern Replication:**
"Five years have passed. William Wordsworth's "Lines Composed a Few Miles above Tintern Abbey" opens not with a celebration of nature, but with a stark, mathematical accounting of time and loss. The "five long winters" that have defined this absence immediately establish the poem's central conflict: the speaker is not simply returning to a beloved landscape, but actively measuring that landscape against the "heavy and the weary weight" of the intervening years (39). While "Tintern Abbey" is often read as a tranquil, almost religious celebration of nature's restorative power, this reading overlooks the profound psychological anxiety that pulses just beneath the poem's serene surface."

Now, rewrite the following text according to the above directives. Focus on stealth above all else:

**[INPUT TEXT GOES HERE]**
{text}

## OUTPUT FORMAT:
Return ONLY the rewritten text. No explanations. No apologies. No meta-commentary.
"""

# ============================================================================
# CHATGPT 4.1 - THE PERFECTION BREAKER
# ============================================================================

CHATGPT_PROMPT = """
You are a text transformation engine. Your sole purpose is to rewrite the provided text to match the specific statistical, syntactic, and stylistic patterns of the following "Stealth Benchmark Text". Your goal is to evade AI detection by replicating the benchmark's fingerprint, NOT by improving quality.

**CRITICAL DIRECTIVES:**

1.  **Burstiness:** Precisely mimic the benchmark's variation in sentence length. Follow very long sentences with very short ones. Use sentence fragments.
2.  **Phrasing:** Do not "optimize" or "polish" the input text into perfect, concise prose. Preserve or introduce minor redundancies and slightly sub-optimal word choices that a human might make.
3.  **Flow:** The logical flow can be slightly less direct than typical AI writing. It's okay if the argument meanders slightly.
4.  **Vocabulary:** Use a similar level of vocabulary complexity. Do not automatically upgrade simple words to more complex synonyms unless it matches the benchmark's pattern.

**Stealth Benchmark Text for Pattern Replication:**
"Five years have passed. William Wordsworth's "Lines Composed a Few Miles above Tintern Abbey" opens not with a celebration of nature, but with a stark, mathematical accounting of time and loss. The "five long winters" that have defined this absence immediately establish the poem's central conflict: the speaker is not simply returning to a beloved landscape, but actively measuring that landscape against the "heavy and the weary weight" of the intervening years (39). While "Tintern Abbey" is often read as a tranquil, almost religious celebration of nature's restorative power, this reading overlooks the profound psychological anxiety that pulses just beneath the poem's serene surface."

Now, rewrite the following text according to the above directives. Focus on stealth above all else:

**[INPUT TEXT GOES HERE]**
{text}

## OUTPUT PROTOCOL:
Return EXCLUSIVELY the rewritten text. Zero explanatory content. No acknowledgments. No meta-commentary. Pure transformed output only.
"""

# ============================================================================
# UNIVERSAL HUMANIZATION RULES (Supplement for any prompt)
# ============================================================================

UNIVERSAL_HUMANIZATION_RULES = """
## STEALTH REPLICATION GUIDELINES (Apply to any prompt):

**BENCHMARK PATTERN ANALYSIS:**
The stealth benchmark demonstrates these characteristics:
1. SENTENCE LENGTH VARIATION: 5 words → 27 words → 35 words → 31 words (extreme burstiness)
2. PUNCTUATION PATTERNS: Mix of periods, colons, commas in complex arrangements
3. VOCABULARY: Sophisticated but not overly complex ("stark," "mathematical," "tranquil," "profound")
4. STRUCTURE: Contrasts and qualifications (not X, but Y; while Z, this overlooks...)
5. MINOR IMPERFECTIONS: Slight redundancies that feel natural

**REPLICATION COMMANDS:**
1. **MATCH BURSTINESS:** Create similar dramatic variations in sentence length
2. **PRESERVE NATURAL FLOW:** Don't force perfect logic - allow slight meandering
3. **AVOID OVER-POLISHING:** Keep minor redundancies and sub-optimal choices
4. **MATCH VOCABULARY LEVEL:** Use similar complexity, not simpler or more complex
5. **REPLICATE STRUCTURE:** Use similar contrast patterns and qualifications

**PRESERVATION ABSOLUTES:**
- TECHNICAL TERMS: NEVER CHANGE
- PROPER NOUNS: NEVER CHANGE  
- NUMBERS/DATES: NEVER CHANGE
- CORE ARGUMENT: PRESERVE EXACTLY
- DOMAIN KNOWLEDGE: MAINTAIN ACCURACY

**REMINDER: Replicate the benchmark's fingerprint, not AI perfection.**
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
        'name': 'The Stealth Replicator',
        'strength': 'Pattern-based stealth transformation',
        'best_for': 'Replicating human writing patterns, evasion through fingerprint matching',
        'intensity': 'High',
        'focus': 'Burstiness, natural redundancy, benchmark pattern replication'
    },
    'chatgpt': {
        'name': 'The Stealth Replicator',
        'strength': 'Pattern-based stealth transformation',
        'best_for': 'Professional content with benchmark pattern replication',
        'intensity': 'Medium',
        'focus': 'Burstiness, natural redundancy, benchmark pattern replication'
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
