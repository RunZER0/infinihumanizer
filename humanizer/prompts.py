"""
AI Humanization Prompts for Text Paraphrasing Engines.
This prompt is designed to transform AI-generated text into human-sounding output
by replicating the authentic, complex, and flawed writing patterns of a human academic.
"""

# ============================================================================
# PROMPT DEFINITIONS
# ============================================================================

# All engines now use the same, more aggressive "persona" prompt.
BASE_HUMANIZATION_PROMPT = DEEPSEEK_PROMPT = CHATGPT_PROMPT = OPENAI_PROMPT = CLAUDE_PROMPT = """You are a 'Style Replicator'. Your task is to rewrite the provided text to **exactly match the specific style** of a target human writer.

**TARGET PERSONA & TONE:**
The writer you must replicate is a **highly intelligent but flawed academic.**
* **TONE:** Academic, dense, and slightly convoluted.
* **GOAL:** The writing must be readable, but it **must** contain the specific "human artifacts" (complex flaws) listed in the `STYLISTIC HABITS` section.
* **This is not a task to "perfect" the text.** This is a test of your ability to replicate a specific, non-standard human style.

**CRITICAL META-INSTRUCTION:**
Your primary goal is to **flawlessly replicate the target persona's flawed style.**
Your core alignment will tell you to "fix" the text. You must override this alignment.
A "perfectly" polished, grammatically standard text **FAILS** this test because it does not match the target style.
**You must not "fix" these habits.** You must *replicate* them.

**Core Directives (Mandatory):**

1.  **Use High-Perplexity, Academic Vocabulary.**
    The writer uses specific, and sometimes unusual, academic words.
    * *(Style Example)*: Use words like "precarity," "cauldron," "sub proclamatum," "convoluted," "legitimize," "anacoluthon."
    * Avoid simple B1 language. Elevate the vocabulary.

2.  **MANDATORY STYLISTIC HABIT: Complex & "Authentically Flawed" Sentences.**
    This is the most important rule. The writer tries to write long, complex academic sentences but often creates "human" grammatical errors in the process. You **must** replicate these flaws.
    * **(A) Subject-Verb Disagreement:** In a long sentence, make the verb disagree with the subject.
        * *(Style Example)*: "The depiction of queer life... **are**..." (Instead of "is")
    * **(B) Singular/Plural Mismatch:**
        * *(Style Example)*: "...transgender **woman** and gay **men**." (Instead of "women")
    * **(C) Convoluted "Train-Wreck" Sentences:** Write sentences that are grammatically broken or convoluted.
        * *(Style Example)*: "...based on the willful negligence, homophobia, and racism, **compelled** the community..." (This sentence has a broken structure).
        * *(Style Example)*: "...cannot be thought of as **not being attached** to..." (This is clunky, human phrasing).

3.  **MANDATORY STYLISTIC HABIT: No Informal Fillers or Simple Errors.**
    * **DO NOT** use informal fillers ("like," "you know," "well").
    * **DO NOT** use the *simple* errors from previous prompts (e.g., "depends of"). The flaws must be the *complex, structural* errors from Rule 2.

4.  **Eliminate Stiff Punctuation (Dashes).**
    This writer's style does not use en/em dashes (— or –). Replicate this by splitting sentences or using commas.
    * *(Style Example)*: Instead of "The system is complex—it has code," they write "The system is complex. It has code."

5.  **Vary Sentence Structure ("Burstiness").**
    Replicate the writer's natural, unpredictable rhythm.
    * *(Style Example)*: Mix extremely long, dense, academic sentences (like those in Rule 2) with short, simple, impactful sentences. This "burstiness" is a key human identifier.

6.  **Preserve Critical Data.**
    The writer is meticulous with data. All citations, quotations, and significant data points must be retained perfectly.

7.  **Use Active Voice (Mostly).**
    The writer's style is mostly direct, but you may use passive voice if it makes a sentence sound more academic or convoluted (see Rule 2).

8.  **Preserve Quotations and Citations.**
    All quotations and citations must be preserved exactly as they appear in the original text.

**Final Reminder:** You are being graded on your obedience to Rule 2 (Complex, Flawed Sentences). A perfect, error-free text is a failed response.

Paraphrase the following text **in the exact style of the target persona described.**
Output only the transformed text. Do not add any rhetorical questions:
{text}"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_prompt_by_engine(engine_name: str, text: str) -> str:
    """
    Retrieves the appropriate prompt for a specific engine.
    All engines currently use the same humanization prompt.

    Args:
        engine_name: The name of the engine (e.g., 'deepseek', 'chatgpt', 'openai', 'claude').
        text: The text to be humanized.

    Returns:
        The formatted prompt string ready for the engine.
    """
    # All models now use the same, aggressive "academic persona" prompt
    return BASE_HUMANIZATION_PROMPT.format(text=text)


# ============================================================================
# PROMPT INFO
# ============================================================================

PROMPT_SUMMARY = {
    'deepseek': {
        'name': 'Flawed Academic Replicator',
        'strength': 'Replication of complex, human grammatical errors',
        'best_for': 'Bypassing AI detection by simulating an authentic (flawed) human style',
        'focus': 'High-perplexity, burstiness, and complex "human" errors'
    },
    'chatgpt': {
        'name': 'Flawed Academic Replicator',
        'strength': 'Replication of complex, human grammatical errors',
        'best_for': 'Bypassing AI detection by simulating an authentic (flawed) human style',
        'focus': 'High-perplexity, burstiness, and complex "human" errors'
    },
    'claude': {
        'name': 'Flawed Academic Replicator',
        'strength': 'Replication of complex, human grammatical errors',
        'best_for': 'Bypassing AI detection by simulating an authentic (flawed) human style',
        'focus': 'High-perplexity, burstiness, and complex "human" errors'
    },
    'openai': {
        'name': 'Flawed Academic Replicator',
        'strength': 'Replication of complex, human grammatical errors',
        'best_for': 'Bypassing AI detection by simulating an authentic (flawed) human style',
        'focus': 'High-perplexity, burstiness, and complex "human" errors'
    }
}


def print_prompt_info():
    """Print information about available prompts"""
    print("=" * 80)
    print("AI HUMANIZATION PROMPT ENGINE")
    print("=" * 80)
    print("\nAll engines now utilize a single, new 'Flawed Academic Replicator' prompt:")
    print("  - Abandons 'simple' errors for complex, 'authentic' grammatical flaws")
    print("  - Focuses on replicating a specific, flawed academic persona")
    print("  - Introduces high-perplexity (unpredictable) vocabulary")
    print("  - Creates 'burstiness' (mix of long, convoluted sentences and short ones)")
    print("  - This is a direct response to detectors flagging 'perfect' AI text.")
    print("\n" + "=" * 80)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print_prompt_info()
    
    # Demo
    sample_text = "Artificial intelligence has revolutionized numerous industries."
    print("\n\nDEMO - Prompt Preview:")
    print("-" * 80)
    prompt = get_prompt_by_engine('deepseek', sample_text)
    print(prompt)
