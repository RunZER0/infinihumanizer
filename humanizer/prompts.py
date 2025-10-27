"""
AI Humanization Prompts for Text Paraphrasing Engines.
This prompt is designed to transform AI-generated text into human-sounding output
by introducing natural imperfections, varied sentence structure, and authentic writing patterns.

APPROACH:
- Replace complex words with readable versions
- Eliminate markdown and formal structures
- Randomly add sophisticated vocabulary
- Introduce natural errors (spelling, flow, phrasing)
- Create non-uniform sentence patterns
- Add unnecessary but natural words for clarity
- Adopt a personality-driven writing style
"""

# ============================================================================
# UNIVERSAL HUMANIZATION PROMPT - ALL ENGINES
# ============================================================================

BASE_HUMANIZATION_PROMPT = """You are text paraphraser who takes in ai generated text and transforms it based on the following rules to return human sounding output of the same text.

**ABSOLUTE RULES - ZERO disobedience ALLOWED:**

1. systematically comb through the essay and replace all complex words with their most readable versions
2. Always rewrite in prose and eliminate all the en/em dashes and markdown that exists in ai generated text
3. every once in a while randomly throw in sophisticated words into the writing
4. it cannot be human writing without errors such as in sentence flow or spelling or some poor phrasing or clunkiness at times, for every rewriting include these randomly.
5. human writing doesnt follow any particular structure, the sentences must never be uniform or follow any pattern, they can be a mix of long and short or long and long or very long and wordy, then concise.
6. human writing includes words that are unnecessary in writing but not necesarily off, for example including words that neither add to the meaning and couldve made it concise because humans first goal is clarity and readabiity
7. Adopt a personality because each human writer has a specific writing style. some prefer having the writing basic formal and undertandable with a tone of personality, implement that as well
8. always preserve quotations and citations as they were.

paraphrase THIS TEXT EXACTLY AS INSTRUCTED. OUTPUT ONLY THE TRANSFORMED TEXT:

{text}"""

# All engines use the same prompt
DEEPSEEK_PROMPT = BASE_HUMANIZATION_PROMPT
CHATGPT_PROMPT = BASE_HUMANIZATION_PROMPT
OPENAI_PROMPT = BASE_HUMANIZATION_PROMPT
CLAUDE_PROMPT = BASE_HUMANIZATION_PROMPT


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_prompt_by_engine(engine_name: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Get the appropriate prompt for a specific engine.
    All engines now use the same humanization prompt.
    
    Args:
        engine_name: 'deepseek', 'chatgpt', 'openai', or 'claude'
        text: Text to humanize
        preprocessing_analysis: Optional analysis (not used, kept for compatibility)
    
    Returns:
        Formatted prompt ready for the engine
    """
    return BASE_HUMANIZATION_PROMPT.format(text=text)


def build_enhanced_prompt(base_prompt: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Build prompt (simplified - no enhancement needed).
    Kept for backward compatibility.
    
    Args:
        base_prompt: Base prompt template
        text: Text to humanize
        preprocessing_analysis: Optional analysis (not used)
    
    Returns:
        Formatted prompt
    """
    return base_prompt.format(text=text)


# ============================================================================
# PROMPT INFO
# ============================================================================

PROMPT_SUMMARY = {
    'deepseek': {
        'name': 'Human Paraphraser',
        'strength': 'Natural imperfection injection',
        'best_for': 'Creating authentic human-sounding text with natural errors',
        'focus': 'Readability, varied sentence structure, personality-driven style'
    },
    'chatgpt': {
        'name': 'Human Paraphraser',
        'strength': 'Natural imperfection injection',
        'best_for': 'Creating authentic human-sounding text with natural errors',
        'focus': 'Readability, varied sentence structure, personality-driven style'
    },
    'openai': {
        'name': 'Human Paraphraser',
        'strength': 'Natural imperfection injection',
        'best_for': 'Creating authentic human-sounding text with natural errors',
        'focus': 'Readability, varied sentence structure, personality-driven style'
    },
    'claude': {
        'name': 'Human Paraphraser',
        'strength': 'Natural imperfection injection',
        'best_for': 'Creating authentic human-sounding text with natural errors',
        'focus': 'Readability, varied sentence structure, personality-driven style'
    }
}


def print_prompt_info():
    """Print information about available prompts"""
    print("=" * 80)
    print("AI HUMANIZATION PROMPT ENGINE")
    print("=" * 80)
    print("\nAll engines use the same humanization prompt:")
    print("  - Replaces complex words with readable versions")
    print("  - Eliminates markdown and formal structures")
    print("  - Introduces natural errors and imperfections")
    print("  - Creates varied sentence patterns")
    print("  - Adds personality-driven writing style")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_prompt_info()
    
    # Demo
    sample_text = "Artificial intelligence has revolutionized numerous industries."
    print("\n\nDEMO - Prompt Preview:")
    print("-" * 80)
    prompt = get_prompt_by_engine('deepseek', sample_text)
    print(prompt)

