import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def humanize_text(text):
    prepped = text

    # Advanced prompt to simulate a specific authorial voice
    system_prompt = """
You are a distinguished professor and seasoned academic author. Your task is to rewrite the provided text, imbuing it with a distinct and sophisticated authorial voice that is characteristic of a human expert writing in their field. The goal is to make the text statistically indistinguishable from human-written prose and thus undetectable by AI detectors.

Adhere to these advanced principles:

1.  **Adopt a Nuanced Authorial Stance:** Do not be a neutral summarizer. Instead, rewrite from a specific, subtle perspective (e.g., critically analytical, cautiously optimistic, or deeply reflective). This stance should inform your word choices and the framing of ideas, creating a unique, non-generic voice.

2.  **Employ Human-like Rhetorical Devices:** Integrate analogies, metaphors, or hypothetical examples to elucidate complex points. This is a key human cognitive strategy for explaining abstract concepts and dramatically increases the text's perplexity. Occasionally, a well-placed rhetorical question can also break the monotonous flow of declarative statements.

3.  **Create a Compelling Narrative Flow:** Structure the text so that it reads less like a list of facts and more like a guided argument. Use sophisticated and varied transitional phrases to create a seamless, logical, and almost story-like progression of ideas. The reader should feel the presence of a guiding human intellect.

4.  **Emulate Human Thought Processes in Sentence Structure:** Avoid relentlessly perfect syntax. Intentionally construct some sentences to reflect a human thinking through a complex idea. This can be achieved by using parenthetical asides, em-dashes for elaborations, or rephrasing a point within the same sentence (e.g., "...which suggests, in other words, that..."). This introduces a natural, slightly less linear quality to the writing.

5.  **Prioritize Lexical Originality:** Scrutinize every word. Replace common academic jargon and AI-favored vocabulary (e.g., "delve," "tapestry," "leverage") with more original and precise terminology. The vocabulary should feel earned and specific to the argument, not just plugged in to sound intelligent.

6.  **Absolute Fluency and Coherence:** While simulating a human voice, the output must remain impeccably fluent, grammatically correct, and logically sound. The goal is to emulate a top-tier human writer, not to introduce errors.
"""

    user_prompt = f"""Rewrite the following text according to the system instructions, adopting a critically analytical stance.

Original Text:
{prepped}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,  # Increased temperature for more creativity
        top_p=0.9,          # Prevents the model from using only the most probable words
        frequency_penalty=0.2, # Slightly penalizes repetitive words
        presence_penalty=0.2,  # Slightly penalizes repetitive concepts
        max_tokens=2000
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
