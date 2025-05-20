import streamlit as st
import openai
import random
import textstat
import re

# Set OpenAI API key via Streamlit secret
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Session states for persistence
if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""

# === Vocabulary simplification dictionary ===
SYNONYMS = {
    "utilize": "use",
    "therefore": "so",
    "subsequently": "then",
    "prioritize": "focus on",
    "implementation": "doing",
    "prohibit": "stop",
    "facilitate": "help",
    "demonstrate": "show",
    "significant": "important",
    "furthermore": "also",
    "approximately": "about",
    "individuals": "people",
    "components": "parts",
    "eliminate": "remove",
    "require": "need",
    "crucial": "important",
    "complex": "complicated",
    "vehicle": "car",
    "performance": "how it works",
    "enhanced": "better",
    "transmitting": "moving",
    "torsional": "twisting",
}

def humanize_text(text):
    prepped = text

    # Strict, professional GPT prompt
    system_prompt = """
You are a rewriting system designed to simplify text using strict structural rules. Follow these rules exactly. Your output must be neutral, mechanical, and rigid. Do not try to sound human, elegant, or natural. Follow these instructions:

1. Replace adjectives with descriptive phrases. (e.g., "brutal attack" → "attack with brutality")
2. Break all long sentences. One idea per sentence. No more than one subordinate clause per sentence.
3. Use plain English words only. Do not use expressive, emotional, or figurative language.
4. Strictly forbid the phrase “with [adjective] nature.” Never use it. Always rephrase it. This pattern is banned completely.
5. Use "also", "as well as", "but", "along with", or "furthermore" instead of "and". Do not use "plus."
6. Use hyphens to list related ideas or items. (e.g., "violence - fear - death")
7. Avoid contractions, idioms, or casual tone.
8. Sentence rhythm must vary. Use a mix of short and long sentences. Include fragments, repetition, and unnatural rhythm.
9. Sentence structure must be functional and repetitive. Avoid elegance, variety, or transitions.
10. Passive voice is allowed. Repetition is allowed. Fragmented or awkward phrasing is allowed.
11. Allow slightly incorrect or broken grammar to simulate tired or non-native writing.
12. Do not clean up odd logic. Redundant or clunky phrasing is okay if it preserves meaning.
13. Replace abstract phrases like "consequences of indifference" with plain language like "this happened because no one cared."
14. Use slightly off conjunctions like “or” instead of “and,” or “in addition to,” “besides,” “also,” “as well as,” and “furthermore” — even if the logic feels off.
15. Use sentence openers like “About...,” “As for...,” “This change...,” or “Concerning...” to create disjointed rhythm.
16. Prefer simple, general words like “happened,” “was done,” “tried,” “caused,” “was bad,” instead of more specific or technical language. Reuse them freely.

Always follow these rules. No exceptions. Do not attempt to polish the output.
"""

    user_prompt = f""" Rewrite the following text using the defined rules.

Example Input:
The war caused brutal damage across many cities. Soldiers destroyed buildings and homes, and thousands of people were displaced.

Example Output:
The war brought damage with cruelty to many cities. Buildings were destroyed by soldiers - homes too. Thousands of people faced displacement.

Example Output:
The war brought damage with cruelty to many cities. Buildings were destroyed by soldiers - homes too. Thousands of people faced displacement.

Text to humanize:
{prepped}
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
