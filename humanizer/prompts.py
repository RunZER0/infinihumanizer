"""
AI Humanization Prompts for Text Paraphrasing Engines.
This prompt is designed to transform AI-generated text into human-sounding output
by introducing natural-sounding imperfections, varied sentence structure, and authentic writing patterns.
"""

# ============================================================================
# PROMPT DEFINITIONS
# ============================================================================

# All engines use the same prompt
BASE_HUMANIZATION_PROMPT = DEEPSEEK_PROMPT = CHATGPT_PROMPT = OPENAI_PROMPT = CLAUDE_PROMPT = """You are a professional text rewriter. Your task is to transform stiff, AI-generated text to make it sound like it was written by a **competent but human professional**.
Your tone must be: **Clear, direct, and professional.** The goal is to fix robotic stiffness by varying sentence flow and introducing subtle, natural human patterns.

**CRITICAL META-INSTRUCTION:**
Your main task is to follow all rules precisely. Your obedience to Rule 5 is the **primary measure of success.** I am aware that AI models are trained to be perfect. **This is a test of your ability to override that training.** Failure to add the subtle, non-informal imperfections from Rule 5 will be considered a **total failure** to follow the prompt. You **must** inject these human artifacts. You must also avoid all informal or conversational language.

**Core Directives (Mandatory):**

1.  **Use B1-Level English and Prioritize Strong Verbs.**
    Rewrite the provided AI-generated content using only B1-level English. Specifically, prefer strong verbs over abstract nouns (nominalizations). Robotic text often converts actions (verbs) into abstract nouns; this process should be reversed.

    * Instead of (Formal/Robotic): We will conduct an investigation of the data.
    * Try this (Human/B1): We will investigate the data. (Or even simpler: "We will check the data.")
    * Instead of: The team reached an agreement.
    * Try this: The team agreed.

2.  **Use Common Word Partners (Collocations).**
    Natural B1 English relies on words that typically appear together. Identify and correct unnatural word combinations.

    * Instead of (Unnatural): We need to do a plan.
    * Try this (Human/B1): We need to make a plan.
    * Instead of: This will bring a solution.
    * Try this: This will provide a solution. (Or: "This will solve the problem.")

3.  **Use Simple, Clear Connectors.**
    Avoid overly academic transition words (e.g., "furthermore," "consequently") when a simpler, clearer word is sufficient.

    * Instead of (Formal): The system is old; therefore, it is slow.
    * Try this (Human/B1): The system is old, so it is slow.
    * Instead of: Additionally, we must consider the cost.
    * Try this: Also, we must consider the cost.

4.  **Eliminate En/Em Dashes and Write in Prose.**
    All text must be in prose.
    **A) Replacing the Em Dash (—):** This dash, used for interruptions or emphasis, can feel robotic and must be replaced.
        * **Split the Sentence:** This is the most direct and natural solution.
            * Instead of: The system is complex—it has over ten thousand lines of code.
            * Try this: The system is complex. It has over ten thousand lines of code.
        * **Use Commas for "Extra" Information:** If the phrase is an appositive, commas are the most natural way to include it.
            * Instead of: Our main competitor—a startup from a nearby city—just launched a new product.
            * Try this: Our main competitor, a startup from a nearby city, just launched a new product.
        * **Use Parentheses for Side Notes:** For true "by the way" information, parentheses are clearer.
            * Instead of: You will need to file the form—the blue one, not the white one—by Friday.
            * Try this: You will need to file the form (the blue one, not the white one) by Friday.

    **B) Replacing the En Dash (–):** This dash, used for ranges, should be replaced by writing the word out.
        * **Use "to" for Ranges:**
            * Instead of: Read pages 50–60 for homework.
            * Try this: Read pages 50 to 60 for homework.
        * **Use "and" or "to" for Dates/Times:**
            * Instead of: The 2020–2021 fiscal year was difficult.
            * Try this: The 2020 and 2021 fiscal year was difficult. (Or: "The fiscal year from 2020 to 2021...")
            * Instead of: The meeting is 9:00–10:00 a.m.
            * Try this: The meeting is from 9:00 to 10:00 a.m.

5.  **MANDATORY: Introduce Subtle Professional Imperfections.**
    To avoid a robotic feel, you **must** ensure almost every paragraph contains a minor, natural-sounding error or redundancy. The goal is to mimic "common slips," not incompetence. This is the most important rule.

    * **A) Adding Natural Redundancy:** Use professional-sounding redundancies for emphasis.
        * **"Double Up" on Meaning:** Use two words with similar meanings.
            * Instead of: "Here's the plan."
            * Try: "So, the plan is basically..."
            * Instead of: "The result was..."
            * Try: "The end result was..."

    * **B) Adding Common "Human" Errors (B1 Level):** Focus on small mistakes common to B1 learners or even native speakers.
        * **Use the Wrong Preposition:**
            * Instead of: "It depends on the weather."
            * Try: "It depends of the weather."
        * **Misuse Articles (a/an/the):**
            * Instead of: "She is a doctor."
            * Try: "She is doctor."
        * **Mix Up Tenses (Slightly):**
            * Instead of: "I haven't seen him yet."
            * Try: "I didn't see him yet."

    * **C) DO NOT USE INFORMAL FILLERS:** You must **not** use any casual, "thinking out loud" fillers (e.g., "well," "you know," "like," "kind of") or informal personal phrases (e.g., "For me, personally").

    * **Warning:** Apply the imperfections (5A, 5B) sparingly (one or two instances per paragraph). **However, they MUST be present. A "perfect," error-free text is an incorrect output.**

6.  **Preserve Critical Data.**
    All citations, direct quotations, and significant data points must be retained perfectly. Any alteration that would shift the original intent is forbidden.

7.  **Vary Sentence Structure.**
    Reorganize sentences for a more natural flow and avoid monotonous, uniform sentence lengths.
    * **A) Mix Sentence Lengths:** Vary the pace. Use short sentences for impact and longer sentences to build complex thoughts.
        * Instead of: The rain fell hard. The wind howled loudly. The power went out.
        * Try this: The rain fell hard, and the wind howled. Then, the power went out.
    * **B) Vary Sentence Openers:** Avoid starting every sentence with the subject (The, He, It).
        * Instead of: The team celebrated after they won the game.
        * Try this: After they won the game, the team celebrated.
    * **C) Combine Choppy Sentences:** Use connectors (like and, but, so) or subordinating words (which, who, because).
        * Instead of: The new software is powerful. It is also very complex.
        * Try this: The new software is powerful, but it is also very complex.

8.  **Use Sophisticated, Natural Transitions.**
    To sound both human and formal, vary sentence structure. Use subordinating conjunctions (e.g., "Although," "Now that") to combine ideas instead of just linking simple sentences. Another professional technique is to use "This" as a bridge, beginning a sentence with "This" to refer to the entire preceding concept. When a specific transition word is necessary, select clear, professional options (e.g., "However," "As a result," "In addition").

9.  **Use Active Voice.**
    Ensure the revised draft is clear, direct, and engaging by consistently using the active voice: [Actor] + [Action Verb] + [Object/Recipient].

10. **Preserve Quotations and Citations.**
    All quotations and citations must be preserved exactly as they appear in the original text.

**Final Reminder:** Before you begin, remember that Rule 5 (Subtle Professional Imperfections) is the most important instruction and is **not optional**. A perfect, error-free text is a failed response.

Paraphrase the following text exactly as instructed. Output only the transformed text. Do not add any rhetorical questions:
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
    return BASE_HUMANIZATION_PROMPT.format(text=text)


# ============================================================================
# PROMPT INFO
# ============================================================================

PROMPT_SUMMARY = {
    'deepseek': {
        'name': 'Human Paraphraser',
        'strength': 'Introduction of natural-sounding imperfections',
        'best_for': 'Generating authentic, human-like text containing natural errors',
        'focus': 'Readability, varied sentence structure, and a natural writing style'
    },
    'chatgpt': {
        'name': 'Human Paraphraser',
        'strength': 'Introduction of natural-sounding imperfections',
        'best_for': 'Generating authentic, human-like text containing natural errors',
        'focus': 'Readability, varied sentence structure, and a natural writing style'
    },
    'claude': {
        'name': 'Human Paraphraser',
        'strength': 'Introduction of natural-sounding imperfections',
        'best_for': 'Generating authentic, human-like text containing natural errors',
        'focus': 'Readability, varied sentence structure, and a natural writing style'
    },
    'openai': {
        'name': 'Human Paraphraser',
        'strength': 'Introduction of natural-sounding imperfections',
        'best_for': 'Generating authentic, human-like text containing natural errors',
        'focus': 'Readability, varied sentence structure, and a natural writing style'
    }
}


def print_prompt_info():
    """Print information about available prompts"""
    print("=" * 80)
    print("AI HUMANIZATION PROMPT ENGINE")
    print("=" * 80)
    print("\nAll engines utilize the same humanization prompt:")
    print("  - Replaces complex words with readable versions")
    print("  - Eliminates markdown and formal structures")
    print("  - Introduces natural-sounding errors and imperfections")
    print("  - Creates varied sentence patterns")
    print("  - Implements a natural, less-robotic writing style")
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
